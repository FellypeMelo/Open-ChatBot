import pytest
from app.core.world import WorldEngine
from datetime import datetime

def test_world_engine_time_context():
    # Mocking a late night time
    night_time = datetime(2026, 5, 7, 23, 30)
    engine = WorldEngine()
    
    context = engine.get_time_context(current_time=night_time)
    
    assert "23:30" in context["time"]
    assert context["is_night"] is True
    assert "sleepy" in context["suggested_mood"].lower()

def test_world_engine_morning_context():
    morning_time = datetime(2026, 5, 7, 8, 30)
    engine = WorldEngine()
    context = engine.get_time_context(current_time=morning_time)
    assert context["is_night"] is False
    assert "energetic" in context["suggested_mood"].lower()

def test_world_engine_afternoon_context():
    afternoon_time = datetime(2026, 5, 7, 14, 30)
    engine = WorldEngine()
    context = engine.get_time_context(current_time=afternoon_time)
    assert context["is_night"] is False
    assert "focused" in context["suggested_mood"].lower()

def test_world_engine_evening_context():
    evening_time = datetime(2026, 5, 7, 20, 30)
    engine = WorldEngine()
    context = engine.get_time_context(current_time=evening_time)
    assert context["is_night"] is False
    assert "relaxed" in context["suggested_mood"].lower()
