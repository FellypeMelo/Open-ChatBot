# C4 Model

Deep-dive diagrams (Context, Container, Component).

## Context
The Context Diagram represents the interactions between the User, the UI, the Backend, the local DB, and the AI Engine.

![Context Diagram](./dp_local_openchatbot.puml)

## Container
The Container Diagram illustrates the macro components of Open-ChatBot.

- **React Frontend**: Main interface.
- **FastAPI Backend**: Logic orchestration, state transitions, API serving.
- **SQLite Database**: Relational storage for chats, states, user profiles.
- **LLM Subsystems**: `llama-server.exe` serving inference & embedding.

## Component
The component boundaries revolve around the routers (Chat, Characters, Tags, Settings, Users) and core engine (LlamaClient, DB).
