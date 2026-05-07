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
