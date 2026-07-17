"""Character-card macro substitution.

Character definitions (persona, scenario, greetings, example dialog) may use
{{char}} / {{user}} placeholders -- the SillyTavern/Tavern-card convention.
Until now these were stored verbatim and never resolved, so a greeting like
"Hello {{user}}" reached the model literally. render_macros resolves them at
prompt-build and greeting-seed time.
"""

import re

_CHAR_RE = re.compile(r"\{\{\s*char\s*\}\}", re.IGNORECASE)
_USER_RE = re.compile(r"\{\{\s*user\s*\}\}", re.IGNORECASE)


def render_macros(text, char_name: str = "", user_name: str = "User") -> str:
    """Replace {{char}} / {{user}} (case-insensitive, whitespace-tolerant) with
    the character and user names. Returns falsy input unchanged."""
    if not text:
        return text
    out = _CHAR_RE.sub(char_name or "", str(text))
    out = _USER_RE.sub(user_name or "User", out)
    return out
