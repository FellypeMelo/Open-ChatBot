from datetime import datetime, timezone
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.backend.core.engine.engine import (
    get_time_context,
    update_needs,
    evolve_character,
    should_be_sleeping,
)
from src.backend.db.models import AgentState, Character, Tag


def test_get_time_context():
    # 1. Null time (covers auto-now datetime.now(timezone.utc))
    res = get_time_context(None)
    assert "time" in res
    assert "is_night" in res

    # 2. Hourly range tests
    # 0 <= hour < 6
    t0 = datetime(2026, 6, 23, 2, 0, tzinfo=timezone.utc)
    assert get_time_context(t0)["suggested_mood"] == "Sleepy and quiet"
    assert get_time_context(t0)["is_night"] is True

    # 6 <= hour < 12
    t6 = datetime(2026, 6, 23, 8, 0, tzinfo=timezone.utc)
    assert get_time_context(t6)["suggested_mood"] == "Energetic and fresh"
    assert get_time_context(t6)["is_night"] is False

    # 12 <= hour < 18
    t12 = datetime(2026, 6, 23, 14, 0, tzinfo=timezone.utc)
    assert get_time_context(t12)["suggested_mood"] == "Focused and productive"

    # 18 <= hour < 22
    t18 = datetime(2026, 6, 23, 20, 0, tzinfo=timezone.utc)
    assert get_time_context(t18)["suggested_mood"] == "Relaxed and winding down"

    # 22 <= hour < 24
    t22 = datetime(2026, 6, 23, 23, 0, tzinfo=timezone.utc)
    assert get_time_context(t22)["suggested_mood"] == "Sleepy and contemplative"
    assert get_time_context(t22)["is_night"] is True


def test_update_needs():
    current_time = datetime(2026, 6, 23, 12, 0, tzinfo=timezone.utc)

    # 1. No last_update
    stats_no_update = {"energy": 100}
    assert update_needs(stats_no_update, current_time) == stats_no_update

    # 2. Update needs with last_update timezone-naive fallback
    naive_last = datetime(2026, 6, 23, 10, 0)  # 2 hours ago
    stats = {
        "energy": 80,
        "hunger": 20,
        "social": 70,
        "happiness": 90,
        "last_update": naive_last.isoformat(),
        "is_sleeping": False,
    }

    res = update_needs(stats, current_time)
    assert res["energy"] < 80  # drained
    assert res["hunger"] > 20  # increased
    assert res["social"] < 70
    assert res["happiness"] < 90

    # 3. Sleeping state recovery
    stats_sleeping = stats.copy()
    stats_sleeping["is_sleeping"] = True
    res_sleep = update_needs(stats_sleeping, current_time)
    assert res_sleep["energy"] > 80  # recovered

    # 4. Aware timezone check
    aware_last = datetime(2026, 6, 23, 11, 0, tzinfo=timezone.utc)
    stats_aware = stats.copy()
    stats_aware["last_update"] = aware_last.isoformat()
    res_aware = update_needs(stats_aware, current_time)
    assert res_aware["energy"] < 80


def test_evolve_character_edge_cases():
    mock_db = MagicMock(spec=Session)

    # 1. Agent not found
    mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None
    evolve_character(mock_db, 1, {"traits": {}})
    mock_db.commit.assert_not_called()

    # Reset mock
    mock_db.reset_mock()

    # Setup mock agent state
    agent_state = AgentState(character_id=1, mood="Neutral")
    agent_state.stats = {
        "energy": 50,
        "relationship": 40,  # invalid, not a dict
    }
    mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = agent_state

    # Mock Character query as well
    mock_char = Character(name="Luna", description="Distant")
    mock_char.tags = []

    # Setup query router
    def mock_query(model):
        q = MagicMock()
        if model == Character:
            q.filter.return_value.first.return_value = mock_char
        elif model == AgentState:
            q.filter.return_value.with_for_update.return_value.first.return_value = (
                agent_state
            )
        return q

    mock_db.query.side_effect = mock_query

    reflection = {
        "traits": ["Quiet"],  # traits is a list
        "summary": "Luna spent time studying.",
        "facts": ["Likes reading", "Likes reading"],  # duplicated fact
        "relationship_change": 10,
        "diary_entry": "I feel slightly closer to Alice.",
    }

    # 2. Evolve execution
    evolve_character(mock_db, 1, reflection)

    # Verify traits list converted
    assert "discovered_traits" in agent_state.stats
    # Verify duplicated facts ignored
    assert agent_state.stats["facts"] == ["Likes reading"]
    # Verify relationship score converted to dict and updated:
    # 40 (invalid format) fallback to 50 + 10 = 60
    assert agent_state.stats["relationship"]["score"] == 60

    # Verify JournalEntry added
    mock_db.add.assert_any_call(agent_state)
    mock_db.commit.assert_called()


def test_evolve_character_tag_swaps():
    mock_db = MagicMock(spec=Session)
    agent_state = AgentState(character_id=1, stats={"relationship": {"score": 50}})

    # Setup Tags
    t_distant = Tag(label="emotionally distant", instruction="Distant instruction")
    t_affectionate = Tag(label="affectionate", instruction="Affectionate instruction")
    t_guarded = Tag(label="guarded", instruction="Guarded instruction")
    t_vulnerable = Tag(label="vulnerable", instruction="Vulnerable instruction")

    # 1. Test score >= 80 evolution (distant -> affectionate, guarded -> vulnerable)
    mock_char_high = Character(name="Luna")
    mock_char_high.tags = [t_distant, t_guarded]

    # Dynamic Query Mocking
    def mock_query(model):
        q = MagicMock()
        if model == Character:
            q.filter.return_value.first.return_value = mock_char_high
        elif model == AgentState:
            q.filter.return_value.with_for_update.return_value.first.return_value = (
                agent_state
            )
        elif model == Tag:
            # Always return None so get_or_create_tag creates new instances in the test context
            q.filter.return_value.first.return_value = None
        return q

    mock_db.query.side_effect = mock_query

    evolve_character(mock_db, 1, {"relationship_change": 40})  # 50 -> 90

    labels = [t.label for t in mock_char_high.tags]
    assert "emotionally distant" not in labels
    assert "guarded" not in labels
    assert "affectionate" in labels
    assert "vulnerable" in labels

    # 2. Test score <= 30 evolution (affectionate -> distant, vulnerable -> guarded)
    mock_db.reset_mock()
    agent_state.stats = {"relationship": {"score": 50}}
    mock_char_low = Character(name="Luna")
    mock_char_low.tags = [t_affectionate, t_vulnerable]

    def mock_query_low(model):
        q = MagicMock()
        if model == Character:
            q.filter.return_value.first.return_value = mock_char_low
        elif model == AgentState:
            q.filter.return_value.with_for_update.return_value.first.return_value = (
                agent_state
            )
        elif model == Tag:
            q.filter.return_value.first.return_value = None
        return q

    mock_db.query.side_effect = mock_query_low

    evolve_character(mock_db, 1, {"relationship_change": -30})  # 50 -> 20

    labels_low = [t.label for t in mock_char_low.tags]
    assert "affectionate" not in labels_low
    assert "vulnerable" not in labels_low
    assert "emotionally distant" in labels_low
    assert "guarded" in labels_low

    # 3. Test evolution exception pathway (db rollback)
    mock_db.reset_mock()
    mock_db.commit.side_effect = Exception("DB error")
    mock_db.query.side_effect = mock_query_low

    evolve_character(mock_db, 1, {"relationship_change": 5})
    mock_db.rollback.assert_called_once()


def test_should_be_sleeping():
    # 1. Low energy sleeping
    assert should_be_sleeping({"energy": 15}, datetime(2026, 6, 23, 12, 0)) is True

    # 2. Late night sleeping (11 PM)
    assert should_be_sleeping({"energy": 80}, datetime(2026, 6, 23, 23, 0)) is True

    # 3. Not sleeping (afternoon, full energy)
    assert should_be_sleeping({"energy": 90}, datetime(2026, 6, 23, 14, 0)) is False
