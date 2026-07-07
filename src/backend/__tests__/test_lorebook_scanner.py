from src.backend.core.context.lorebook_scanner import LorebookScanner
from src.backend.db.models import Character, LorebookEntry


def _make_entry(db_session, **kwargs):
    """Create and persist a LorebookEntry with sane defaults for tests."""
    defaults = dict(
        keyword="",
        keys=[],
        secondary_keys=[],
        content="",
        character_id=None,
        is_global=False,
        insertion_order=100,
        probability=100,
        scan_depth=5,
        is_constant=False,
        cooldown_turns=0,
    )
    defaults.update(kwargs)
    entry = LorebookEntry(**defaults)
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


def test_keyword_regex_match_triggers_entry(db_session):
    entry = _make_entry(
        db_session,
        keyword="sword",
        keys=["sword"],
        content="The Sword of Destiny is legendary.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("I draw my SWORD now.", character_id=999)

    assert result == [entry.content]


def test_no_match_returns_empty_list(db_session):
    _make_entry(
        db_session,
        keyword="dragon",
        keys=["dragon"],
        content="Dragons are dangerous.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("I like cats.", character_id=1)

    assert result == []


def test_global_entry_applies_regardless_of_character(db_session):
    entry = _make_entry(
        db_session,
        keyword="moon",
        keys=["moon"],
        content="The moon lore.",
        is_global=True,
        character_id=None,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("I look at the moon.", character_id=42)

    assert result == [entry.content]


def test_character_scoped_entry_only_triggers_for_its_own_character(db_session):
    char_a = Character(name="A", description="d")
    char_b = Character(name="B", description="d")
    db_session.add_all([char_a, char_b])
    db_session.commit()

    entry = _make_entry(
        db_session,
        keyword="sword",
        keys=["sword"],
        content="Char A's sword lore.",
        is_global=False,
        character_id=char_a.id,
    )
    scanner = LorebookScanner(db_session)

    result_a = scanner.scan_and_extract("I hold a sword.", character_id=char_a.id)
    assert result_a == [entry.content]

    # Not global and belongs to a different character -> must not trigger.
    result_b = scanner.scan_and_extract("I hold a sword.", character_id=char_b.id)
    assert result_b == []


def test_constant_entry_included_without_text_match_when_probability_is_100(
    db_session,
):
    entry = _make_entry(
        db_session,
        content="Always present lore.",
        is_global=True,
        is_constant=True,
        probability=100,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("completely unrelated text", character_id=1)

    assert result == [entry.content]


def test_constant_entry_excluded_when_probability_is_zero(db_session):
    _make_entry(
        db_session,
        content="Never present lore.",
        is_global=True,
        is_constant=True,
        probability=0,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("anything at all", character_id=1)

    assert result == []


def test_matched_keyword_entry_excluded_when_probability_is_zero(db_session):
    _make_entry(
        db_session,
        keyword="wolf",
        keys=["wolf"],
        content="Wolf lore.",
        is_global=True,
        probability=0,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("A wolf howls in the distance.", character_id=1)

    assert result == []


def test_invalid_regex_falls_back_to_plain_substring_match(db_session):
    entry = _make_entry(
        db_session,
        keys=["[unclosed(regex"],
        content="Fallback lore triggered.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract(
        "this text has [unclosed(regex right in it", character_id=1
    )

    assert result == [entry.content]


def test_invalid_regex_fallback_does_not_match_absent_substring(db_session):
    _make_entry(
        db_session,
        keys=["[unclosed(regex"],
        content="Fallback lore not triggered.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("nothing relevant appears here", character_id=1)

    assert result == []


def test_no_keys_falls_back_to_keyword_field(db_session):
    entry = _make_entry(
        db_session,
        keyword="castle",
        keys=[],
        content="Castle lore.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("We approach the CASTLE gates.", character_id=1)

    assert result == [entry.content]


def test_no_keys_and_no_keyword_never_matches(db_session):
    _make_entry(
        db_session,
        keyword=None,
        keys=[],
        content="Should never appear.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("random unrelated text", character_id=1)

    assert result == []


def test_insertion_order_controls_result_ordering(db_session):
    entry_second = _make_entry(
        db_session,
        keys=["alpha"],
        content="Second content (order 20)",
        is_global=True,
        insertion_order=20,
    )
    entry_first = _make_entry(
        db_session,
        keys=["alpha"],
        content="First content (order 5)",
        is_global=True,
        insertion_order=5,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("alpha alpha alpha", character_id=1)

    assert result == [entry_first.content, entry_second.content]


def test_multiple_keys_matches_on_later_key(db_session):
    entry = _make_entry(
        db_session,
        keys=["zzz-no-match-zzz", "griffin"],
        content="Griffin lore.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    result = scanner.scan_and_extract("A griffin flies overhead.", character_id=1)

    assert result == [entry.content]


def test_secondary_keys_currently_have_no_effect(db_session):
    """Documents current (likely unintended) behavior: LorebookEntry.secondary_keys
    is defined on the model but scan_and_extract() never reads it anywhere. An
    entry configured with a secondary key that is absent from the scanned text
    still fires purely off the primary `keys` match. If AND-gating on
    secondary keys is ever implemented, this test should be updated to assert
    the new (gated) behavior.
    """
    entry = _make_entry(
        db_session,
        keys=["potion"],
        secondary_keys=["healing"],
        content="Potion lore.",
        is_global=True,
    )
    scanner = LorebookScanner(db_session)

    # "healing" (the secondary key) is intentionally absent from the text.
    result = scanner.scan_and_extract("I drink a potion.", character_id=1)

    assert result == [entry.content]


def test_cooldown_turns_currently_have_no_effect(db_session):
    """Documents current (likely unintended) behavior: LorebookEntry.cooldown_turns
    is defined on the model but scan_and_extract() never tracks turn state or
    suppresses re-triggering. Calling scan_and_extract repeatedly with the
    same matching text fires the entry every time, even with a nonzero
    cooldown_turns configured.
    """
    entry = _make_entry(
        db_session,
        keys=["torch"],
        content="Torch lore.",
        is_global=True,
        cooldown_turns=5,
    )
    scanner = LorebookScanner(db_session)

    first = scanner.scan_and_extract("I light a torch.", character_id=1)
    second = scanner.scan_and_extract("I light a torch.", character_id=1)

    assert first == [entry.content]
    assert second == [entry.content]
