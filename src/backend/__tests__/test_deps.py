from src.backend.core import deps
from src.backend.core.deps import (
    llama_client,
    vector_store,
    brain,
    get_llama_client,
    get_vector_store,
    get_brain,
)
from src.backend.core.engine.llm import LlamaClient
from src.backend.core.memory.vector_store import VectorStore
from src.backend.core.orchestration.bridge import Brain


def test_module_level_singletons_are_the_expected_types():
    # The composition root should build exactly one instance of each type.
    assert isinstance(llama_client, LlamaClient)
    assert isinstance(vector_store, VectorStore)
    assert isinstance(brain, Brain)


def test_get_llama_client_returns_module_singleton_by_identity():
    assert get_llama_client() is llama_client
    # Calling it again must not construct a new instance.
    assert get_llama_client() is deps.llama_client


def test_get_vector_store_returns_module_singleton_by_identity():
    assert get_vector_store() is vector_store
    assert get_vector_store() is deps.vector_store


def test_get_brain_returns_module_singleton_by_identity():
    assert get_brain() is brain
    assert get_brain() is deps.brain


def test_singletons_are_wired_together():
    # vector_store must share the same llama_client instance, otherwise
    # routers built from different getters would use separate HTTP
    # connection pools (the exact regression this module prevents).
    assert vector_store.llm_client is llama_client

    # brain must operate on the shared vector_store instance...
    assert brain.vector_store is vector_store

    # ...and, since deps.py builds Brain without an explicit llm_client,
    # Brain falls back to vector_store.llm_client, so brain.llm must also
    # resolve back to the very same llama_client singleton.
    assert brain.llm is llama_client


def test_chat_router_and_brain_share_the_patched_test_vector_store():
    # conftest.py's autouse mock_vector_store_path fixture must redirect BOTH
    # chat.vector_store (used by add_memory/delete_by_message_ids) AND
    # brain.vector_store (used internally by build_prompt's RAG retrieval) to
    # the same isolated per-test instance -- otherwise a memory written via
    # one is invisible to a read via the other for the rest of the test run.
    from src.backend.api import chat as chat_module

    assert chat_module.brain.vector_store is chat_module.vector_store
    # And confirm the fixture actually replaced the module-level singleton
    # (not a no-op that left both pointed at the unpatched deps.vector_store).
    assert chat_module.vector_store is not deps.vector_store
