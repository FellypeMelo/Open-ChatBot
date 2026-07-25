import httpx
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.backend.core.config import settings
from src.backend.core.context.budget import (
    ContextBudgetCalculator,
    _configured_context_size,
)


def test_configured_context_size_uses_runner_value():
    """When the runner singleton exposes a context size, it should be used."""
    mock_runner = MagicMock()
    mock_runner.config = {"inference": {"context_size": 4096}}

    with patch("src.backend.core.engine.runner.runner", mock_runner):
        assert _configured_context_size() == 4096


def test_configured_context_size_falls_back_on_exception():
    """If reading the runner's config raises, fall back to settings.CONTEXT_SIZE."""
    mock_runner = MagicMock()
    mock_runner.config = None  # subscripting None raises TypeError

    with patch("src.backend.core.engine.runner.runner", mock_runner):
        assert _configured_context_size() == settings.CONTEXT_SIZE


def test_calculator_defaults_to_configured_context_size():
    """Constructing without an explicit size picks up the configured/fallback size."""
    mock_runner = MagicMock()
    mock_runner.config = {"inference": {"context_size": 5000}}

    with patch("src.backend.core.engine.runner.runner", mock_runner):
        calc = ContextBudgetCalculator()

    assert calc.context_size == 5000
    assert calc.usable_budget == 5000 - settings.RESPONSE_SLOT - settings.TOKEN_PADDING


def test_calculator_explicit_context_size_overrides_configured_value():
    """An explicit context_size argument takes priority over the configured size."""
    mock_runner = MagicMock()
    mock_runner.config = {"inference": {"context_size": 5000}}

    with patch("src.backend.core.engine.runner.runner", mock_runner):
        calc = ContextBudgetCalculator(context_size=1234)

    assert calc.context_size == 1234
    assert calc.usable_budget == 1234 - settings.RESPONSE_SLOT - settings.TOKEN_PADDING


@pytest.mark.asyncio
async def test_get_budget_shape_and_history_budget():
    """get_budget returns the expected keys, and history_budget is usable_budget
    minus the sum of the fixed allocations."""
    calc = ContextBudgetCalculator(context_size=8192)
    budget = await calc.get_budget()

    fixed_cost = sum(calc.allocations.values())

    assert budget["total_context"] == 8192
    assert budget["response_slot"] == settings.RESPONSE_SLOT
    assert budget["padding"] == settings.TOKEN_PADDING
    assert budget["usable_budget"] == calc.usable_budget
    assert budget["allocations"] == calc.allocations
    assert budget["history_budget"] == calc.usable_budget - fixed_cost
    assert budget["history_budget"] == max(0, calc.usable_budget - fixed_cost)


@pytest.mark.asyncio
async def test_history_budget_capped_at_window_on_large_context():
    # EPIC Phase 4: with ~40k of room at 48k context, raw history is bounded to
    # the effective window so a 4B doesn't drown in the middle.
    calc = ContextBudgetCalculator(context_size=49152)
    budget = await calc.get_budget()
    assert budget["history_budget"] == settings.HISTORY_WINDOW_TOKENS


def test_allocations_reserve_anchor_and_realistic_card():
    """Phase 0: the card reserve is no longer the tiny 300 (which under-counted a
    real card), and the recency anchor is reserved so fixed_cost matches what
    build_prompt actually emits."""
    calc = ContextBudgetCalculator(context_size=49152)
    assert "anchor" in calc.allocations
    assert calc.allocations["anchor"] == settings.ANCHOR_TOKENS
    assert calc.allocations["character_def"] >= 1500
    assert calc.allocations["mes_example"] >= 1000


@pytest.mark.asyncio
async def test_count_tokens_empty_string_returns_zero_without_http_call():
    """An empty string short-circuits and never touches the network."""
    calc = ContextBudgetCalculator(context_size=8192)

    with patch.object(httpx.AsyncClient, "post", AsyncMock()) as mock_post:
        result = await calc.count_tokens("")

    assert result == 0
    mock_post.assert_not_called()


@pytest.mark.asyncio
async def test_count_tokens_success_returns_exact_token_count():
    """A 200 response returns the length of the tokens list from the server."""
    calc = ContextBudgetCalculator(context_size=8192)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tokens": [1, 2, 3, 4]}

    with patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_response)):
        result = await calc.count_tokens("hello world")

    assert result == 4


@pytest.mark.asyncio
async def test_count_tokens_non_200_falls_back_to_word_estimate():
    """A non-200 response falls back to a word-count-based estimate."""
    calc = ContextBudgetCalculator(context_size=8192)

    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_response)):
        text = "one two three four"
        result = await calc.count_tokens(text)

    assert result == int(len(text.split()) * 1.3)


@pytest.mark.asyncio
async def test_count_tokens_exception_falls_back_to_word_estimate():
    """An exception raised while calling the tokenize endpoint also falls back
    to the word-count-based estimate."""
    calc = ContextBudgetCalculator(context_size=8192)

    with patch.object(
        httpx.AsyncClient,
        "post",
        AsyncMock(side_effect=httpx.ConnectError("connection refused")),
    ):
        text = "one two three four five"
        result = await calc.count_tokens(text)

    assert result == int(len(text.split()) * 1.3)


# --- validate_final_prompt: real-tokenizer check on the FINAL assembled -------
# --- prompt against the model's actual context window -------------------------


@pytest.mark.asyncio
async def test_validate_final_prompt_skipped_under_testing():
    """Under settings.TESTING (the default in this whole suite), the check must
    never touch the network -- same early-return pattern as llm.py's embed()."""
    calc = ContextBudgetCalculator(context_size=100)
    assert settings.TESTING is True

    with patch.object(httpx.AsyncClient, "post", AsyncMock()) as mock_post:
        await calc.validate_final_prompt("anything")

    mock_post.assert_not_called()


@pytest.mark.asyncio
async def test_validate_final_prompt_warns_when_over_budget(caplog, monkeypatch):
    """An assembled prompt whose real token count exceeds context_size logs a
    warning with the actual vs. budget counts."""
    # alembic's env.py runs logging.config.fileConfig() (test_alembic_reconcile
    # exercises that path), which -- with its default disable_existing_loggers
    # -- permanently disables every logger already created at that point,
    # including this module's. That is a real, pre-existing cross-test/process
    # hazard unrelated to this feature; re-enable defensively so this
    # assertion doesn't depend on suite run order.
    from src.backend.core.context import budget as budget_module

    monkeypatch.setattr(budget_module.logger, "disabled", False)
    calc = ContextBudgetCalculator(context_size=100)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tokens": list(range(150))}

    with (
        patch.object(settings, "TESTING", False),
        patch.object(settings, "E2E_TESTING", False),
        patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_response)),
    ):
        with caplog.at_level(logging.WARNING):
            await calc.validate_final_prompt("a very long assembled prompt")

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "150" in warnings[0].message
    assert "100" in warnings[0].message


@pytest.mark.asyncio
async def test_validate_final_prompt_no_warning_when_under_budget(caplog):
    """An assembled prompt within context_size logs nothing."""
    calc = ContextBudgetCalculator(context_size=100)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tokens": list(range(50))}

    with (
        patch.object(settings, "TESTING", False),
        patch.object(settings, "E2E_TESTING", False),
        patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_response)),
    ):
        with caplog.at_level(logging.WARNING):
            await calc.validate_final_prompt("a short assembled prompt")

    assert not [r for r in caplog.records if r.levelno == logging.WARNING]


@pytest.mark.asyncio
async def test_validate_final_prompt_swallows_tokenize_failure(caplog):
    """A /tokenize failure (server unreachable) must not raise and must not
    warn -- there is no real count to compare against."""
    calc = ContextBudgetCalculator(context_size=100)

    with (
        patch.object(settings, "TESTING", False),
        patch.object(settings, "E2E_TESTING", False),
        patch.object(
            httpx.AsyncClient,
            "post",
            AsyncMock(side_effect=httpx.ConnectError("connection refused")),
        ),
    ):
        with caplog.at_level(logging.WARNING):
            await calc.validate_final_prompt("anything")  # must not raise

    assert not [r for r in caplog.records if r.levelno == logging.WARNING]
