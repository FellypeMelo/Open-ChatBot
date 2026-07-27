# Architecture Overview

High-level system design for Open-ChatBot.

## Architecture Drivers
1. **Local Execution & Privacy**: The system runs entirely locally, without dependencies on cloud models, to guarantee maximum privacy. It uses a local consolidated `llama.cpp` server.
2. **Modularity & Stateful Agents**: AI characters have dedicated state (mood, energy, relationship, location), enabling dynamic role-play and persistent memories.
3. **Responsiveness & Aesthetics**: High-end React/Vite frontend with Tailwind CSS ensuring a sleek, anti-slop, fast and mobile-responsive interface.
4. **Testability & Maintainability**: Strict enforcement of >80% code coverage, decoupled architecture using FastAPI and SQLAlchemy.

## System Architecture
Open-ChatBot operates as a local monolithic application with decoupled functional units. It consists of:
- **Frontend SPA**: React, TypeScript, Vite, Tailwind CSS. Served statically in production or via Vite in dev.
- **Backend API**: Python FastAPI providing RESTful routes.
- **Database**: SQLite (`chatbot.db`) managed via SQLAlchemy ORM.
- **AI Core (Consolidated Llama-Server)**: A single background process running `llama-server.exe` with the `--embedding` flag enabled, serving both completion and embedding generation (RAG) capabilities on a single port (default 8080), saving massive RAM/VRAM resource allocation.

## Key Components
- **LlamaClient**: A Python interface to orchestrate HTTP requests to the single local `llama.cpp` server for both completion and embedding generation.
- **Engine Runner**: The core script (`src/backend/core/engine/runner.py`) responsible for spinning up and tearing down the single `llama.cpp` server subprocess dynamically.
- **Message Tree (Nodes)**: Messages are stored as a tree (`MessageNode`), allowing branching and alternative generation paths.
- **AgentState**: A highly detailed model representing the live conditions (e.g., happiness, hunger, clothing, location) of the Character.
