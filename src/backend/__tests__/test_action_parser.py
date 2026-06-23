import pytest
from src.backend.db.models import AgentState
from src.backend.api.chat import parse_actions_to_state

def test_parse_location():
    state = AgentState(character_id=1, location="Living Room")
    ai_response = "I'm bored here. **walks into the Kitchen** and looks for a snack."
    parse_actions_to_state(ai_response, state)
    assert state.location == "Kitchen"

def test_parse_clothes():
    state = AgentState(character_id=1, clothes="Casual")
    ai_response = "Wait a second. *She disappears for a moment and* **changes into a red dress**. \"How do I look?\""
    parse_actions_to_state(ai_response, state)
    assert state.clothes == "Red dress"

def test_parse_multiple():
    state = AgentState(character_id=1, location="Bedroom", clothes="Pajamas")
    ai_response = "*Yawning, she* **enters the garden** while she **is wearing a light cloak** over her shoulders."
    parse_actions_to_state(ai_response, state)
    assert state.location == "Garden"
    assert state.clothes == "Light cloak"

def test_parse_no_match():
    state = AgentState(character_id=1, location="Forest")
    ai_response = "The trees are beautiful today."
    parse_actions_to_state(ai_response, state)
    assert state.location == "Forest"

def test_parse_eating():
    state = AgentState(character_id=1)
    state.stats["hunger"] = 70
    ai_response = "I was so hungry! *Happily* **eats an apple** and grins."
    parse_actions_to_state(ai_response, state)
    assert state.stats["hunger"] == 40

def test_parse_sleeping():
    state = AgentState(character_id=1)
    state.stats["is_sleeping"] = False
    ai_response = "*Yawning deeply,* **goes to sleep** on the sofa."
    parse_actions_to_state(ai_response, state)
    assert state.stats["is_sleeping"] is True

def test_parse_waking():
    state = AgentState(character_id=1)
    state.stats["is_sleeping"] = True
    ai_response = "*As the morning sun shines,* **wakes up** and stretches."
    parse_actions_to_state(ai_response, state)
    assert state.stats["is_sleeping"] is False
