# Design: llama.cpp Integration (Frontend-Driven Configuration)

**Status:** Draft
**Date:** 2026-05-28
**Topic:** LLM Integration

## 1. Overview
Enable users to configure their `llama.cpp` server connection directly from the frontend. The application will act as a proxy, sending the user-provided model name and server URL to the backend, which then communicates with the `llama.cpp` instance.

## 2. Approach: Dynamic Request Context
We will implement a "Connection Settings" system where the frontend maintains the active LLM configuration and passes it with every request.

### 2.1 Frontend Changes
- **Settings Store**: Use `localStorage` to persist `model_name` and `base_url` (defaulting to `http://localhost:8080`).
- **Settings UI**: 
    - Add a "Settings" button to the `Sidebar`.
    - Create a `SettingsModal` or expand `UserProfileModal` to include LLM configuration fields.
- **API Service**: Update `src/frontend/src/services/api.ts` to accept an optional `config` object in chat requests.

### 2.2 Backend Changes
- **API Schema**: Update `ChatRequest` in `src/backend/api/chat.py` to include optional `model_name` and `base_url` fields.
- **LlamaClient**: Update `src/backend/core/engine/llm.py` to allow passing a dynamic URL and model for each request.
- **OpenAI Compatibility**: Shift `LlamaClient` to use the `/v1/chat/completions` style if needed, or simply ensure the provided `model_name` is passed in the payload for servers that support multi-model routing.

## 3. Data Flow
1. User enters `model_name` (e.g., `Qwen3.5-2B.Q4_K_S.gguf`) and `base_url` in the frontend UI.
2. Frontend saves these to `localStorage`.
3. When the user sends a message, the frontend includes these settings in the POST `/chat` or `/chat/stream` request.
4. The backend's `chat` router receives the request, initializes/configures the `LlamaClient` with the provided parameters, and calls the external `llama.cpp` server.
5. The response is returned to the frontend as usual.

## 4. Error Handling
- **Connection Refused**: If the backend cannot reach the user-provided URL, it returns a specific 502/504 error with a helpful message ("Could not connect to llama.cpp at [URL]").
- **Missing Configuration**: If no configuration is provided, the backend falls back to its `.env` defaults.

## 5. Security
- We will only allow `base_url` values that point to local or private network ranges (default behavior of `httpx` and `llama.cpp` usually involves local hosting, but we should be aware of SSRF risks if this were a public web service).
