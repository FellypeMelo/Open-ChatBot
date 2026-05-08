import pytest
from app.core.world import WorldEngine
from datetime import datetime, timedelta

def test_energy_drain_and_sleep():
    engine = WorldEngine()
    # Initial state: 100 energy at 10 AM
    initial_stats = {"energy": 100, "last_update": datetime(2026, 5, 7, 10, 0).isoformat()}
    
    # 10 hours later at 8 PM
    current_time = datetime(2026, 5, 7, 20, 0)
    new_stats = engine.update_energy(initial_stats, current_time)
    
    assert new_stats["energy"] < 100
    
    # Late night with low energy -> should sleep
    sleep_time = datetime(2026, 5, 7, 23, 30)
    is_sleeping = engine.should_be_sleeping(new_stats, sleep_time)
    assert is_sleeping is True

def test_energy_recovery():
    engine = WorldEngine()
    # Initial state: 10 energy, Asleep at 11 PM
    initial_stats = {
        "energy": 10, 
        "last_update": datetime(2026, 5, 7, 23, 0).isoformat(),
        "is_sleeping": True
    }
    
    # 6 hours later at 5 AM
    current_time = datetime(2026, 5, 8, 5, 0)
    new_stats = engine.update_energy(initial_stats, current_time)
    
    # Recovered 10 per hour * 6 hours = 60. Total 10 + 60 = 70.
    assert new_stats["energy"] == 70
    assert new_stats["is_sleeping"] is True

def test_sleep_triggers():
    engine = WorldEngine()
    
    # Trigger 1: Energy < 20
    low_energy_stats = {"energy": 15}
    day_time = datetime(2026, 5, 7, 14, 0) # 2 PM
    assert engine.should_be_sleeping(low_energy_stats, day_time) is True
    
    # Trigger 2: Time 11 PM - 6 AM
    high_energy_stats = {"energy": 90}
    night_time = datetime(2026, 5, 7, 23, 30) # 11:30 PM
    assert engine.should_be_sleeping(high_energy_stats, night_time) is True
    
    # No trigger: High energy during day
    normal_stats = {"energy": 90}
    afternoon_time = datetime(2026, 5, 7, 14, 0)
    assert engine.should_be_sleeping(normal_stats, afternoon_time) is False
