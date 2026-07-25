import logging
from typing import Dict, Any, Optional
import httpx
from src.backend.core.config import settings

logger = logging.getLogger(__name__)

# Fallback token estimate when the llama-server /tokenize endpoint is unreachable:
# English averages ~1.3 tokens per whitespace-delimited word.
_WORD_TO_TOKEN_RATIO = 1.3


def _estimate_tokens_from_words(text: str) -> int:
    """Rough offline token estimate from the word count."""
    return int(len(text.split()) * _WORD_TO_TOKEN_RATIO)


def _configured_context_size() -> int:
    """The llama-server context size actually in effect (models_config.json,
    editable from the Settings UI), falling back to Settings.CONTEXT_SIZE only
    when the runner isn't available (e.g. an isolated unit test)."""
    try:
        from src.backend.core.engine.runner import runner

        return int(runner.config["inference"]["context_size"])
    except Exception:
        return settings.CONTEXT_SIZE


class ContextBudgetCalculator:
    def __init__(
        self,
        llama_url: str = settings.LLAMA_SERVER_URL,
        context_size: Optional[int] = None,
    ):
        self.llama_url = llama_url
        self.context_size = (
            context_size if context_size is not None else _configured_context_size()
        )
        self.response_slot = settings.RESPONSE_SLOT
        self.padding = settings.TOKEN_PADDING
        self.usable_budget = self.context_size - self.response_slot - self.padding

        # Fixed layer allocations (max caps). These must stay in sync with the
        # layers build_prompt actually caps via allocations.get(...): every key
        # build_prompt reads is reserved here so fixed_cost reflects the real
        # prompt, and no key is reserved for a layer the template never emits
        # (PB-04).
        self.allocations = {
            "system_prompt": 200,
            # Realistic reserve for the card block (identity + persona + scenario)
            # of a typical filled card. The per-field HARD ceiling is
            # settings.CARD_MAX_TOKENS (enforced in build_prompt); this value is
            # only the budget-accounting reserve. A card larger than this eats
            # into history_budget rather than overflowing the window -- fine on a
            # large context, and honest instead of the old 300 that under-counted
            # a real card by ~600-1200 tok.
            "character_def": 1600,
            "user_persona": 100,
            "lorebook_cap": 500,
            "chat_summary": 200,
            "dynamic_state": 60,
            # Recency anchor (persona voice + current scene) reserved so
            # fixed_cost reflects the layer build_prompt actually emits.
            "anchor": settings.ANCHOR_TOKENS,
            # RAG memory layer: build_prompt caps it at allocations["memory"],
            # but it was missing here, so fixed_cost under-counted by ~400 tok and
            # history_budget was over-allocated -> risk of overflowing context.
            "memory": 400,
            # Few-shot example dialogue is the strongest voice lever on a small
            # model; reserve a realistic slice (the hard per-field ceiling is
            # still settings.CARD_MAX_TOKENS in build_prompt).
            "mes_example": 1000,
        }

    async def count_tokens(self, text: str) -> int:
        """Call llama-server /tokenize endpoint to get exact token count."""
        if not text:
            return 0

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.llama_url}/tokenize", json={"content": text}, timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    tokens = data.get("tokens", [])
                    return len(tokens)
                else:
                    logger.warning(
                        f"Tokenize endpoint failed with {response.status_code}. "
                        "Falling back to word-count estimate."
                    )
                    return _estimate_tokens_from_words(text)
        except Exception as e:
            logger.error(
                f"Error calling tokenize endpoint: {e}. "
                "Falling back to word-count estimate."
            )
            return _estimate_tokens_from_words(text)

    async def validate_final_prompt(self, prompt: str) -> None:
        """Best-effort REAL token-count check of the fully assembled prompt
        against the model's actual context window, via llama-server's
        /tokenize endpoint. Every allocation above this is only the len//4
        heuristic, so a long card + history + RAG recall can still silently
        exceed the real window with no signal -- this is the final backstop.

        Skipped under TESTING/E2E_TESTING (no llama-server running), matching
        llm.py's embed()/complete_stream() early-return pattern. Any other
        /tokenize failure (server unreachable, non-200) is caught and skipped
        too: this check must never raise or block prompt assembly.
        """
        if settings.TESTING or settings.E2E_TESTING:
            return
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.llama_url}/tokenize", json={"content": prompt}, timeout=5.0
                )
            if response.status_code != 200:
                return
            actual_tokens = len(response.json().get("tokens", []))
        except Exception as e:
            logger.debug(f"Skipping final prompt token validation: {e}")
            return

        if actual_tokens > self.context_size:
            logger.warning(
                "Assembled prompt (%s tokens) exceeds the configured context_size "
                "(%s tokens) by %s tokens -- the model will silently drop or "
                "truncate context. Reduce card/history/RAG size or increase "
                "context_size.",
                actual_tokens,
                self.context_size,
                actual_tokens - self.context_size,
            )

    async def get_budget(self) -> Dict[str, Any]:
        """Returns the current usable budget and allocations."""
        fixed_cost = sum(self.allocations.values())
        # Reserve a minimum share of the usable budget for conversation history.
        # Otherwise, on a small/quantized context (usable < fixed_cost) history
        # silently floors to 0 and the character loses all turn-to-turn recall.
        min_history = max(
            0, int(self.usable_budget * settings.MIN_HISTORY_BUDGET_RATIO)
        )
        history_budget = self.usable_budget - fixed_cost
        if history_budget < min_history:
            logger.warning(
                "Fixed prompt allocations (%s tok) leave only %s tok for history "
                "on a usable budget of %s; flooring history to the minimum reserve "
                "%s. Increase context_size to avoid dropping fixed layers.",
                fixed_cost,
                history_budget,
                self.usable_budget,
                min_history,
            )
            history_budget = min_history
        history_budget = max(0, min(history_budget, self.usable_budget))

        # Cap the effective raw-history window even when the context is huge: a
        # 4B attends poorly to the middle of a giant window, so feeding it ~40k of
        # raw turns buries the persona/anchor. Bound it; turns older than the
        # window are carried by the rolling summary + RAG, not dumped raw (EPIC
        # Phase 4). On a small context this is a no-op (history is already below
        # the window).
        history_budget = min(history_budget, settings.HISTORY_WINDOW_TOKENS)

        return {
            "total_context": self.context_size,
            "response_slot": self.response_slot,
            "padding": self.padding,
            "usable_budget": self.usable_budget,
            "allocations": self.allocations,
            "history_budget": history_budget,
        }
