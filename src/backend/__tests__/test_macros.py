"""Tests for {{char}}/{{user}} macro substitution (character-card macros)."""

import asyncio
import types
from unittest.mock import AsyncMock, MagicMock

from src.backend.core.context.macros import render_macros
from src.backend.core.orchestration.bridge import Brain


def test_render_macros_basic():
    out = render_macros(
        "Hi {{user}}, I am {{char}}.", char_name="Aria", user_name="Sam"
    )
    assert out == "Hi Sam, I am Aria."


def test_render_macros_case_and_whitespace_insensitive():
    out = render_macros("{{Char}} greets {{ USER }}", char_name="Aria", user_name="Sam")
    assert out == "Aria greets Sam"


def test_render_macros_handles_empty_and_missing_names():
    assert render_macros("") == ""
    assert render_macros(None) is None
    assert render_macros("{{user}}") == "User"  # default user name


def test_build_prompt_resolves_macros_in_persona():
    vs = MagicMock()
    vs.llm_client = MagicMock()
    vs.llm_client.url = "http://127.0.0.1:8080"
    vs.query_memory = AsyncMock(return_value={"documents": [[]]})
    brain = Brain(vs)
    brain.budget_calc.get_budget = AsyncMock(
        return_value={"history_budget": 4096, "allocations": {}}
    )

    char = types.SimpleNamespace(
        id=1,
        name="Aria",
        nickname=None,
        short_description="",
        description="",
        persona_prompt="{{char}} always remembers {{user}}.",
        scenario=None,
        mes_example=None,
        tags=[],
    )
    user = types.SimpleNamespace(
        name="Sam", gender="Unknown", appearance=None, persona_description=None
    )
    state = {
        "location": "x",
        "mood": "y",
        "stats": {"energy": 100, "hunger": 0, "relationship": {"score": 50}},
        "active_summary": "",
    }

    prompt = asyncio.run(brain.build_prompt("hi", char, state, user=user))
    assert "Aria always remembers Sam." in prompt
    assert "{{char}}" not in prompt and "{{user}}" not in prompt
