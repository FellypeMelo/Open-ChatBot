import pytest
from src.backend.core.engine.engine import get_time_context, update_needs
from datetime import datetime, timedelta

def test_time_context_night():
    # Mocking a late night time
    night_time = datetime(2026, 5, 7, 23, 30)
    context = get_time_context(current_time=night_time)
    
    assert "23:30" in context["time"]
    assert context["is_night"] is True
    assert "sleepy" in context["suggested_mood"].lower()

def test_time_context_morning():
    morning_time = datetime(2026, 5, 7, 8, 30)
    context = get_time_context(current_time=morning_time)
    assert context["is_night"] is False
    assert "energetic" in context["suggested_mood"].lower()

def test_time_context_afternoon():
    afternoon_time = datetime(2026, 5, 7, 14, 30)
    context = get_time_context(current_time=afternoon_time)
    assert context["is_night"] is False
    assert "focused" in context["suggested_mood"].lower()

def test_time_context_evening():
    evening_time = datetime(2026, 5, 7, 20, 30)
    context = get_time_context(current_time=evening_time)
    assert context["is_night"] is False
    assert "relaxed" in context["suggested_mood"].lower()

def test_needs_update():
    start_time = datetime(2026, 5, 7, 10, 0)
    end_time = datetime(2026, 5, 7, 12, 0) # 2 hours later
    
    stats = {
        "energy": 100,
        "hunger": 0,
        "happiness": 100,
        "social": 100,
        "is_sleeping": False,
        "last_update": start_time.isoformat()
    }
    
    updated = update_needs(stats, end_time)
    
    # ENERGY_DRAIN_RATE = 5.0 -> 100 - (2 * 5) = 90
    assert updated["energy"] == 90
    # HUNGER_INCREASE_RATE = 10.0 -> 0 + (2 * 10) = 20
    assert updated["hunger"] == 20
    # SOCIAL_DECREASE_RATE = 5.0 -> 100 - (2 * 5) = 90
    assert updated["social"] == 90
    # HAPPINESS_DECREASE_RATE = 2.0 -> 100 - (2 * 2) = 96
    assert updated["happiness"] == 96
    assert updated["last_update"] == end_time.isoformat()

def test_should_be_sleeping():
    from src.backend.core.engine.engine import should_be_sleeping
    
    # 1. Low energy
    assert should_be_sleeping({"energy": 10}, datetime(2026, 5, 7, 12, 0)) is True
    
    # 2. Late night
    assert should_be_sleeping({"energy": 100}, datetime(2026, 5, 7, 23, 30)) is True
    
    # 3. Normal day, high energy
    assert should_be_sleeping({"energy": 100}, datetime(2026, 5, 7, 12, 0)) is False
