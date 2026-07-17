import re
import random
from typing import List

# A key made only of word characters/spaces is a plain literal, not an
# author-written regex. Anything else (|, ., *, [], ...) is treated as an
# intentional regex and used verbatim.
_PLAIN_KEY = re.compile(r"^[\w\s]+$")


def _key_to_pattern(key: str) -> str:
    """Turn a lore key into the pattern actually searched. Plain-literal keys get
    word-boundary anchors so 'cat' matches 'cat' but not 'category' (LB-02);
    keys with regex metacharacters are honored as authored."""
    stripped = key.strip()
    if _PLAIN_KEY.match(stripped):
        return r"\b" + re.escape(stripped) + r"\b"
    return key


class LorebookScanner:
    """
    V2 Lorebook Engine.
    Replaces basic semantic search with precise regex-based keyword scanning,
    probability checks, and recursion limits (depth).
    """

    def __init__(self, db_session):
        self.db = db_session

    def scan_and_extract(self, recent_text: str, character_id: int) -> List[str]:
        """
        Scans the recent text for regex keys associated with the character or global lore.
        Returns a formatted list of lore texts to inject into the prompt.
        """
        from src.backend.db.models import LorebookEntry

        # 1. Fetch relevant entries (character specific + global)
        entries = (
            self.db.query(LorebookEntry)
            .filter(
                (LorebookEntry.character_id == character_id)
                | (LorebookEntry.is_global == True)
            )
            .order_by(LorebookEntry.insertion_order.asc())
            .all()
        )

        active_lore = []

        for entry in entries:
            # 1. Check if it's a constant
            if entry.is_constant:
                if random.randint(1, 100) <= entry.probability:
                    active_lore.append(entry.content)
                continue

            # 2. Check keys via regex
            matched = False
            if entry.keys:
                for key_pattern in entry.keys:
                    # An empty/blank pattern makes re.search match every message
                    # (and "" in text is always True), injecting this lore on
                    # every single turn. Skip it.
                    if not key_pattern or not str(key_pattern).strip():
                        continue
                    try:
                        # Case-insensitive, word-boundary match for plain keys;
                        # explicit regex keys are honored as authored (LB-02).
                        if re.search(
                            _key_to_pattern(str(key_pattern)),
                            recent_text,
                            re.IGNORECASE,
                        ):
                            matched = True
                            break
                    except re.error:
                        # Fallback to plain text match if regex is invalid
                        if key_pattern.lower() in recent_text.lower():
                            matched = True
                            break
            else:
                # If no keys but it's not constant, use keyword as fallback key
                if entry.keyword and entry.keyword.lower() in recent_text.lower():
                    matched = True

            if matched:
                if random.randint(1, 100) <= entry.probability:
                    active_lore.append(entry.content)

        return active_lore
