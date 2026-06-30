import re
import logging

logger = logging.getLogger(__name__)


def validate_narrative_formatting(text: str) -> bool:
    """
    Validates that long responses ( > 50 words) contain at least
    one internal thought (*italic*) and one physical action (**bold**).

    As per RN-003: Any AI output that fails to include at least one Thought
    or Action in a response longer than 50 words is flagged.
    """
    word_count = len(text.split())
    if word_count <= 50:
        return True  # Short responses are exempt

    # Check for Thoughts: *text* (excluding **text**)
    # We use a negative lookbehind/lookahead for * to ensure it's not a double asterisk
    has_thought = bool(re.search(r"(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*)", text))

    # Check for Actions: **text**
    has_action = bool(re.search(r"\*\*.+?\*\*", text))

    is_valid = has_thought and has_action

    if not is_valid:
        logger.warning(
            f"Narrative Validation Failed (words={word_count}): has_thought={has_thought}, has_action={has_action}"
        )

    return is_valid
