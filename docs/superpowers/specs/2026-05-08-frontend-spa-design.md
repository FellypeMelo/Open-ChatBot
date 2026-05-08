# Design Spec: Open-ChatBot Frontend SPA Implementation

## 1. Overview
The goal is to build a single-page application (SPA) frontend that integrates chat, character management, and tag taxonomies into a cohesive, immersive experience using React and Vite.

## 2. Architecture
- **Tech Stack:** React (TypeScript), Vite, Tailwind CSS.
- **State Management:** React Context API for cross-component state (Navigation, Shared Character Data).
- **Navigation:** Client-side routing to switch between `ChatView`, `CharactersView`, and `TagManagementView`.

## 3. Core Components
- **Shell:** Sidebar navigation and persistent application container.
- **ChatView:** Immersion-focused interface with the sequence-based message renderer.
- **CharactersView:** Grid layout for characters with creation/edit modals.
- **TagManagementView:** Organized CRUD interface for tags, grouped by type.

## 4. Implementation Shards
- **Shard 1: Shell & Navigation:** Base SPA layout and routing.
- **Shard 2: Tag Taxonomy:** Tag management and storage.
- **Shard 3: Character Management:** Character creation, editing, and initial stat assignment.
- **Shard 4: Immersion Chat Renderer:** Message parsing and rendering.

## 5. Testing Strategy (TDD)
- All components will follow the Red-Green-Refactor loop.
- Use `vitest` and `@testing-library/react`.
- E2E flow testing for character creation and chat interaction.

## 6. Definitions
- **Character Schema:** `{id, name, description, personality, avatar, stats: {energy, hunger, relationship}}`
- **Tag Schema:** `{id, name, description, type: "Personality" | "Setting" | "Status"}`
