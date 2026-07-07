from src.backend.core.orchestration.validator import validate_narrative_formatting


def test_short_response_exempt():
    text = "Hello there. I am just a short response."
    assert validate_narrative_formatting(text) is True


def test_long_response_valid():
    text = (
        '*I wonder what they want.* "I am happy to see you." '
        "**She walks toward the window** and looks outside at the falling rain. "
        "The atmosphere is quiet today, almost too quiet, and I find myself "
        "thinking about the events of yesterday. *Maybe I should ask.* "
        '"Would you like some tea?" **She turns back with a smile.** '
        "This is a long response intended to exceed fifty words to test "
        "the narrative formatting rules defined in the business specification "
        "known as RN-003, ensuring immersion remains high."
    )
    assert validate_narrative_formatting(text) is True


def test_long_response_missing_thought():
    text = (
        '"I am happy to see you." '
        "**She walks toward the window** and looks outside at the falling rain. "
        "The atmosphere is quiet today, almost too quiet, and I find myself "
        "thinking about the events of yesterday. "
        '"Would you like some tea?" **She turns back with a smile.** '
        "This is a long response intended to exceed fifty words to test "
        "the narrative formatting rules defined in the business specification "
        "known as RN-003, ensuring immersion remains high. It has actions but no thoughts."
    )
    assert validate_narrative_formatting(text) is False


def test_long_response_missing_action():
    text = (
        '*I wonder what they want.* "I am happy to see you." '
        "She walks toward the window and looks outside at the falling rain. "
        "The atmosphere is quiet today, almost too quiet, and I find myself "
        "thinking about the events of yesterday. *Maybe I should ask.* "
        '"Would you like some tea?" She turns back with a smile. '
        "This is a long response intended to exceed fifty words to test "
        "the narrative formatting rules defined in the business specification "
        "known as RN-003, ensuring immersion remains high. It has thoughts but no actions."
    )
    assert validate_narrative_formatting(text) is False
