import re
import random
from typing import List, Optional

# A key made only of word characters/spaces is a plain literal, not an
# author-written regex. Anything else (|, ., *, [], ...) is treated as an
# intentional regex and used verbatim.
_PLAIN_KEY = re.compile(r"^[\w\s]+$")

# Fallback scan depth (recent messages) when an entry doesn't set one.
_DEFAULT_SCAN_DEPTH = 5


def _key_to_pattern(key: str) -> str:
    """Turn a lore key into the pattern actually searched. Plain-literal keys get
    word-boundary anchors so 'cat' matches 'cat' but not 'category' (LB-02);
    keys with regex metacharacters are honored as authored."""
    stripped = key.strip()
    if _PLAIN_KEY.match(stripped):
        return r"\b" + re.escape(stripped) + r"\b"
    return key


def _any_key_matches(keys, text: str) -> bool:
    """True if any non-blank key in `keys` matches `text` (case-insensitive,
    word-boundary for plain keys, regex for authored patterns, plain-substring
    fallback for invalid regex)."""
    if not keys:
        return False
    for key_pattern in keys:
        if not key_pattern or not str(key_pattern).strip():
            # An empty/blank pattern would match every message -- skip it.
            continue
        try:
            if re.search(_key_to_pattern(str(key_pattern)), text, re.IGNORECASE):
                return True
        except re.error:
            if str(key_pattern).lower() in text.lower():
                return True
    return False


class LorebookScanner:
    """
    V2 Lorebook Engine.
    Regex-based keyword scanning with probability checks, per-entry scan depth
    (how many recent messages to consider) and secondary-key selective logic
    (an entry fires only when a primary AND a secondary key both match).
    """

    def __init__(self, db_session):
        self.db = db_session

    def scan_and_extract(
        self,
        recent_text: str,
        character_id: int,
        history: Optional[List[str]] = None,
        turn_index: Optional[int] = None,
        cooldowns: Optional[dict] = None,
    ) -> List[str]:
        """Scan recent conversation for regex keys of the character's (and global)
        lore and return the lore texts to inject.

        `recent_text` is the current turn's text; `history` is the prior recent
        message contents (most-recent-last). Each entry scans the last
        `entry.scan_depth` of those messages (LB-01 scan_depth). Entries with
        `secondary_keys` require both a primary and a secondary match before
        firing (LB-01 selective logic).

        When `turn_index` and a mutable `cooldowns` map ({entry_id: last_fired
        turn}) are supplied, a keyed entry that fired within its `cooldown_turns`
        window is suppressed, and a fresh fire records the turn -- so the same
        lore isn't re-injected every turn (LB-01 cooldown). The caller owns and
        persists `cooldowns`; without it the scanner is stateless as before."""
        from src.backend.db.models import LorebookEntry

        cooldown_enabled = turn_index is not None and cooldowns is not None

        entries = (
            self.db.query(LorebookEntry)
            .filter(
                (LorebookEntry.character_id == character_id)
                | (LorebookEntry.is_global == True)  # noqa: E712
            )
            .order_by(LorebookEntry.insertion_order.asc())
            .all()
        )

        # Most-recent-last window of message texts available to scan.
        messages = [m for m in (history or [])] + [recent_text]

        active_lore = []
        for entry in entries:
            # Constant entries bypass key scanning entirely.
            if entry.is_constant:
                if random.randint(1, 100) <= entry.probability:
                    active_lore.append(entry.content)
                continue

            depth = (
                entry.scan_depth if (entry.scan_depth or 0) > 0 else _DEFAULT_SCAN_DEPTH
            )
            scan_text = "\n".join(m for m in messages[-depth:] if m)

            # Primary match: any key (or the keyword fallback when no keys).
            if entry.keys:
                matched = _any_key_matches(entry.keys, scan_text)
            elif entry.keyword:
                matched = entry.keyword.lower() in scan_text.lower()
            else:
                matched = False

            # Selective logic: a secondary key must ALSO match (LB-01).
            if matched and entry.secondary_keys:
                matched = _any_key_matches(entry.secondary_keys, scan_text)

            if not matched:
                continue

            # Cooldown: skip an entry that fired within its cooldown_turns window
            # so the same lore isn't re-injected every turn (LB-01).
            entry_id = getattr(entry, "id", None)
            on_cooldown = (
                cooldown_enabled
                and entry_id is not None
                and (entry.cooldown_turns or 0) > 0
            )
            if on_cooldown:
                last = cooldowns.get(str(entry_id))
                if last is not None and (turn_index - last) < entry.cooldown_turns:
                    continue

            if random.randint(1, 100) <= entry.probability:
                active_lore.append(entry.content)
                if on_cooldown:
                    cooldowns[str(entry_id)] = turn_index

        return active_lore
