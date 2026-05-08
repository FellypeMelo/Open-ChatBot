from app.core.evolution import get_behavioral_modifiers

def test_get_behavioral_modifiers_exhausted():
    stats = {"energy": 15}
    mods = get_behavioral_modifiers(stats)
    assert "EXHAUSTED: You are barely able to speak. Short sentences, slurred words." in mods

def test_get_behavioral_modifiers_tired():
    stats = {"energy": 40}
    mods = get_behavioral_modifiers(stats)
    assert "Tired, low initiative." in mods

def test_get_behavioral_modifiers_starving():
    stats = {"hunger": 85}
    mods = get_behavioral_modifiers(stats)
    assert "STARVING: You are irritable, distracted by thoughts of food, and very impatient." in mods

def test_get_behavioral_modifiers_relationship_stranger():
    stats = {"relationship": 10}
    mods = get_behavioral_modifiers(stats)
    assert "You are cold, distant, and formal. You don't trust the user." in mods

def test_get_behavioral_modifiers_relationship_acquaintance():
    stats = {"relationship": 30}
    mods = get_behavioral_modifiers(stats)
    assert "You are polite but guarded. You keep things professional." in mods

def test_get_behavioral_modifiers_relationship_friend():
    stats = {"relationship": 60}
    mods = get_behavioral_modifiers(stats)
    assert "You are warm, open, and enjoy their company. You can be more yourself." in mods

def test_get_behavioral_modifiers_relationship_intimate():
    stats = {"relationship": 90}
    mods = get_behavioral_modifiers(stats)
    assert "You are deeply affectionate, playful, and vulnerable. You trust them completely." in mods

def test_get_behavioral_modifiers_multiple():
    stats = {
        "energy": 10,
        "hunger": 90,
        "relationship": 10
    }
    mods = get_behavioral_modifiers(stats)
    assert "EXHAUSTED" in mods
    assert "STARVING" in mods
    assert "cold, distant" in mods
    assert len(mods.split("\n")) == 3
