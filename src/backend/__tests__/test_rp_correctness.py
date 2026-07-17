"""RP correctness regression tests (batch 1: state / reflection / compression /
lorebook). Each test targets a concrete failure mode found in the deep app
analysis. All isolated: no llama-server, no real DB, no vector store.
"""

import asyncio
import types
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.backend.core.context.compressor import compress_state
from src.backend.core.engine.engine import evolve_character, update_needs
from src.backend.core.context.lorebook_scanner import LorebookScanner
from src.backend.db.models import AgentState


# --- Reflection / evolution -------------------------------------------------

def test_evolve_character_traits_do_not_overwrite_core_stats():
    """A reflection whose 'traits' happen to contain a core stat key (energy,
    relationship, ...) must not clobber real state."""
    agent = MagicMock()
    agent.stats = {"energy": 100, "hunger": 10, "relationship": {"score": 50}}
    agent.active_summary = ""
    agent.mood = "Neutral"

    def query_side_effect(model):
        q = MagicMock()
        if model is AgentState:
            q.filter.return_value.with_for_update.return_value.first.return_value = agent
        else:  # Character (tag evolution) -> skip
            q.filter.return_value.first.return_value = None
        return q

    db = MagicMock()
    db.query.side_effect = query_side_effect

    evolve_character(
        db, 1, {"traits": {"energy": 5, "relationship": "corrupt", "mischief": "high"}}
    )

    assert agent.stats["energy"] == 100, "core stat 'energy' was overwritten by a trait"
    assert isinstance(agent.stats["relationship"], dict), "relationship dict was clobbered"
    assert agent.stats.get("mischief") == "high", "non-core trait should still merge"


def test_roll_active_summary_dedups_repeated_line():
    # RF-01: the same (possibly hallucinated) reflection claim must not compound
    # every cycle -- re-appending an identical line is skipped.
    from src.backend.core.engine.engine import _roll_active_summary

    s1 = _roll_active_summary("", "The user loves pirates")
    s2 = _roll_active_summary(s1, "The user loves pirates")

    assert s2.count("The user loves pirates") == 1


def test_active_summary_ages_out_unreinforced_lines():
    # RF-01 (option B, rolling digest): a one-off (possibly hallucinated) claim
    # that is never restated must age out of the rolling window over time,
    # instead of being injected into every future prompt forever.
    from src.backend.core.engine.engine import (
        _roll_active_summary,
        ACTIVE_SUMMARY_MAX_LINES,
    )

    s = _roll_active_summary("", "The user is my spouse")  # unreinforced claim
    for i in range(ACTIVE_SUMMARY_MAX_LINES + 3):
        s = _roll_active_summary(s, f"real observed event {i}")

    assert "The user is my spouse" not in s


def test_merge_reflection_traits_protection_is_case_insensitive():
    # RF-07: an aliased core key ('Energy', 'Relationship') must be rejected too,
    # not leak into stats where a case-sensitive reader could later collide.
    from src.backend.core.engine.engine import _merge_reflection_traits

    stats = {"energy": 100, "relationship": {"score": 50}}
    _merge_reflection_traits(
        stats, {"Energy": 5, "Relationship": "corrupt", "mischief": "high"}
    )

    assert "Energy" not in stats
    assert "Relationship" not in stats
    assert stats["energy"] == 100
    assert stats["relationship"] == {"score": 50}
    assert stats["mischief"] == "high"


# --- State compression ------------------------------------------------------

def test_compress_state_handles_none_stats():
    # Must not raise AttributeError on None.get(...). With no usable stats but a
    # known location/mood, keep grounding the model in those instead of dropping
    # everything to "Unknown" (PB-03).
    out = compress_state({"stats": None, "location": "x", "mood": "y"})
    assert "x" in out and "y" in out
    # Truly empty (no loc/mood either) still collapses to Unknown.
    assert compress_state({"stats": None}) == "State: Unknown"


def test_compress_state_handles_nondict_relationship():
    out = compress_state(
        {"stats": {"energy": 50, "hunger": 0, "relationship": "not-a-dict"}, "location": "Office", "mood": "Calm"}
    )
    assert isinstance(out, str) and "Office" in out


def test_compress_state_injects_learned_facts_and_traits():
    # RF-03: reflection extracts facts/traits and stores them, but they were
    # never surfaced to the model, so the character 'forgot' them every turn.
    out = compress_state(
        {
            "location": "X",
            "mood": "Y",
            "stats": {
                "energy": 100,
                "relationship": {"score": 50},
                "facts": ["user's name is Alice", "allergic to cats"],
                "discovered_traits": ["curious"],
            },
        },
        "User",
    )
    assert "Alice" in out
    assert "allergic to cats" in out
    assert "curious" in out


def test_compress_state_high_energy_reads_as_alert():
    # Bidirectional physicality: energy 97% must surface as ENERGIZED, not leave
    # the model to write the character frail (which contradicted the HUD).
    out = compress_state(
        {"location": "X", "mood": "Y",
         "stats": {"energy": 97, "hunger": 0, "relationship": {"score": 50}}},
        "User",
    )
    assert "ENERGIZED" in out


def test_compress_state_warmth_modulates_without_overriding_voice():
    # The warmth band is a dial expressed in the character's own voice, not the
    # old generic "Polite but reserved" that homogenized every character.
    out = compress_state(
        {"location": "X", "mood": "Y",
         "stats": {"energy": 50, "hunger": 0, "relationship": {"score": 40}}},
        "Bob",
    )
    assert "in your own voice" in out
    assert "40%" in out  # score stays visible
    assert "Polite but reserved" not in out


# --- Time-decay after clear -------------------------------------------------

def test_clear_chat_history_keeps_stats_able_to_decay():
    """clear_chat_history reset stats must include 'last_update', otherwise
    update_needs early-returns forever and needs freeze after 'New Chat'."""
    import src.backend.api.chat as chatmod

    fake_vs = MagicMock()
    fake_vs.clear_character_memories = AsyncMock(return_value=0)
    db = MagicMock()
    state = MagicMock()
    state.stats = None
    db.query.return_value.filter.return_value.first.return_value = state

    with patch.object(chatmod, "vector_store", fake_vs):
        asyncio.run(chatmod.clear_chat_history(1, db=db))

    assert "last_update" in state.stats, "reset stats missing last_update -> decay disabled"
    later = datetime.fromisoformat(state.stats["last_update"]) + timedelta(hours=3)
    decayed = update_needs(state.stats, later)
    assert decayed["hunger"] > state.stats["hunger"], "hunger should rise over 3h; decay is dead"


# --- Lorebook scanner -------------------------------------------------------

def _lore_entry(**kw):
    base = dict(
        is_constant=False,
        keys=[],
        secondary_keys=[],
        keyword="",
        probability=100,
        scan_depth=5,
        content="LORE",
    )
    base.update(kw)
    return types.SimpleNamespace(**base)


def _scanner_with(entries):
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = entries
    return LorebookScanner(db)


def test_lorebook_empty_key_does_not_match_everything():
    """An empty-string key must not regex-match every message (re.search('', x)
    matches anything), which would inject that lore into every single turn."""
    scanner = _scanner_with([_lore_entry(keys=[""], content="POISON")])
    out = scanner.scan_and_extract("a totally unrelated sentence", 1)
    assert "POISON" not in out


def test_lorebook_real_key_still_matches():
    scanner = _scanner_with([_lore_entry(keys=["dragon"], content="Dragons breathe fire")])
    out = scanner.scan_and_extract("I saw a dragon today", 1)
    assert out == ["Dragons breathe fire"]


def test_lorebook_plain_key_matches_whole_word_not_substring():
    # LB-02: a plain-word key must match on a word boundary, not as a substring.
    # 'cat' firing on 'category' injects unrelated lore into every such turn --
    # a silent poison source. The scanner's own comment already claims word-
    # boundary matching; make the behavior match the claim.
    scanner = _scanner_with([_lore_entry(keys=["cat"], content="CATLORE")])
    assert "CATLORE" not in scanner.scan_and_extract("what is your category?", 1)
    assert scanner.scan_and_extract("i have a cat", 1) == ["CATLORE"]


def test_lorebook_explicit_regex_key_is_honored_as_authored():
    # A key containing regex metacharacters is an intentional author-written
    # pattern and must be used verbatim (no word-boundary wrapping).
    scanner = _scanner_with([_lore_entry(keys=["drag.n"], content="DRAGON")])
    assert scanner.scan_and_extract("i saw a dragon", 1) == ["DRAGON"]


def test_lorebook_scan_depth_scans_recent_history():
    # LB-01 scan_depth: an entry with depth 3 fires on a key that appeared two
    # turns ago (within the window), not only in the current message.
    scanner = _scanner_with([_lore_entry(keys=["castle"], scan_depth=3, content="CASTLE")])
    # Window = last 3 of [history..., current]: castle sits inside it.
    history = ["long ago", "we rode to the castle", "then it rained"]
    out = scanner.scan_and_extract("good night", 1, history=history)
    assert out == ["CASTLE"]


def test_lorebook_scan_depth_excludes_older_messages():
    # A key older than the scan_depth window must NOT fire.
    scanner = _scanner_with([_lore_entry(keys=["castle"], scan_depth=2, content="CASTLE")])
    history = ["we rode to the castle", "then it rained", "we made camp"]
    # Window = last 2 of [history..., current] -> "we made camp","good night".
    out = scanner.scan_and_extract("good night", 1, history=history)
    assert out == []


def test_lorebook_secondary_keys_require_both_to_match():
    # LB-01 selective logic: entry fires only when a primary AND a secondary key
    # both match the scan window.
    scanner = _scanner_with(
        [_lore_entry(keys=["king"], secondary_keys=["betrayal"], content="PLOT")]
    )
    # Primary only -> no fire.
    assert scanner.scan_and_extract("long live the king", 1) == []
    # Primary + secondary -> fire.
    assert scanner.scan_and_extract("the king spoke of betrayal", 1) == ["PLOT"]
