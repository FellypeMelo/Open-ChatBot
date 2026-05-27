import pytest
from src.backend.core.orchestration.evolution import get_tier_instructions, get_forced_modifiers

def test_tier_stranger():
    instructions = get_tier_instructions(10)
    assert "STRANGER" in instructions
    assert "Formal" in instructions
    assert "Maintain professional or distant boundaries" in instructions

def test_tier_acquaintance():
    instructions = get_tier_instructions(35)
    assert "ACQUAINTANCE" in instructions
    assert "Polite" in instructions
    assert "Civil, slightly detached" in instructions

def test_tier_friend():
    instructions = get_tier_instructions(65, user_nickname="Buddy")
    assert "FRIEND" in instructions
    assert "Warm" in instructions
    assert "Buddy" in instructions
    assert "Physical touch is acceptable" in instructions

def test_tier_intimate():
    instructions = get_tier_instructions(95, user_nickname="Darling")
    assert "INTIMATE" in instructions
    assert "Deep Bond" in instructions
    assert "Darling" in instructions
    assert "Vulnerable and deeply connected" in instructions

def test_tier_boundaries():
    # 20 is still Stranger
    assert "STRANGER" in get_tier_instructions(20)
    # 21 is Acquaintance
    assert "ACQUAINTANCE" in get_tier_instructions(21)
    # 50 is Acquaintance
    assert "ACQUAINTANCE" in get_tier_instructions(50)
    # 51 is Friend
    assert "FRIEND" in get_tier_instructions(51)
    # 80 is Friend
    assert "FRIEND" in get_tier_instructions(80)
    # 81 is Intimate
    assert "INTIMATE" in get_tier_instructions(81)

def test_forced_modifiers_exhaustion():
    stats = {"energy": 5}
    mods = get_forced_modifiers(stats)
    assert "CRITICAL EXHAUSTION" in mods
    assert "on the verge of collapse" in mods

def test_forced_modifiers_starvation():
    stats = {"hunger": 95}
    mods = get_forced_modifiers(stats)
    assert "STARVING" in mods
    assert "primal need for food" in mods

def test_forced_modifiers_none():
    stats = {"energy": 100, "hunger": 0, "happiness": 100}
    mods = get_forced_modifiers(stats)
    assert mods == ""
