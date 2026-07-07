import logging
from typing import Dict, Any, Optional
import httpx
from src.backend.core.config import settings

logger = logging.getLogger(__name__)


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

        # Fixed layer allocations (max caps)
        self.allocations = {
            "system_prompt": 200,
            "character_def": 300,
            "user_persona": 100,
            "lorebook_cap": 500,
            "chat_summary": 200,
            "post_history": 200,
            "dynamic_state": 60,
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
                        f"Tokenize endpoint failed with {response.status_code}. Fallback to word count * 1.3"
                    )
                    return int(len(text.split()) * 1.3)
        except Exception as e:
            logger.error(
                f"Error calling tokenize endpoint: {e}. Fallback to word count * 1.3"
            )
            return int(len(text.split()) * 1.3)

    async def get_budget(self) -> Dict[str, Any]:
        """Returns the current usable budget and allocations."""
        fixed_cost = sum(self.allocations.values())
        history_budget = max(0, self.usable_budget - fixed_cost)

        return {
            "total_context": self.context_size,
            "response_slot": self.response_slot,
            "padding": self.padding,
            "usable_budget": self.usable_budget,
            "allocations": self.allocations,
            "history_budget": history_budget,
        }
