# Claude Instructions & Corrections Log

## Essential Rules & Preferences
1. **Package Manager**: ALWAYS use `pnpm` (never `npm` or `yarn`) for all frontend operations, dependencies, and script runs (e.g., `pnpm test`, `pnpm dev`, `pnpm install`).
2. **Environment & Shell**: Running on Windows (win32) using PowerShell. Always write PowerShell-compatible command syntax (e.g., `Remove-Item` instead of `rm`, `New-Item` instead of `touch`).
3. **Database Rules**: Do not access the production database (`chatbot.db`) during testing. Ensure tests are fully isolated.
4. **Test Coverage**: Maintain at least 80% test coverage for both frontend and backend codebases (overall and per major module/file). Ensure new features include corresponding tests.
5. **Design Taste & Mobile Responsiveness**: Follow high-end anti-slop visual standards. Keep hero sections within viewport using `min-h-[100dvh]` instead of `h-screen`. Prefer CSS Grid over flexbox math (`grid grid-cols-...`). Ensure mobile navigation menu is clean, responsive, and collapses gracefully on screens `< 768px` (using sidebar drawer or modal hamburger patterns).

## Project Context
We are working on **Open-ChatBot**, a stateful, modular AI character platform.
- **Backend**: Python (FastAPI/pytest). Uses `llama-server.exe` for model inference and embeddings (configured in `models_config.json`).
- **Frontend**: React + TypeScript + Vite + TailwindCSS.
- **Last Status**: Integrated dynamic server configuration and model selection for llama.cpp, implemented Settings UI, and updated ChatView/App components.

## Corrections Log
| Date | Model / User Action | Correction / Mistake Made | Why It Happened & How to Avoid |
| :--- | :--- | :--- | :--- |
| 2026-06-22 | User Correction | Tried using `npm run test` instead of `pnpm`. | Under-specified initial package manager preference. Resolved: Always use `pnpm` in this workspace. |

## Frontend Design Taste Guidelines
1. **Responsiveness & Layouts**:
   - VIEWPORT STABILITY: Use `min-h-[100dvh]` instead of `h-screen` for hero sections.
   - CSS GRID over flexbox math: Avoid complex percent widths (`w-[calc(...)]`). Use CSS Grid (`grid grid-cols-1 md:grid-cols-2 gap-md`).
   - Mobile menus must collapse cleanly under `< 768px` using overlay sidebars or modals.
2. **Typography**:
   - Sans font selection: Prefer `Outfit` for sans display/headlines and `JetBrains Mono` for mono. Avoid `Inter` as the default choice.
   - Single-family emphasis: Use bold/italic of the same family inside headers. Avoid mixing serif and sans-serif inside the same header block.
3. **Color Calibration**:
   - Restrained saturation: Max 1 accent color with neutral bases (Zinc/Stone/Slate).
   - Theme Lock: The layout has one theme. Individual sections do not flip themes (e.g., no light-mode segment sandwiched inside a dark-mode page).
4. **Interactive Controls & CTAs**:
   - Contrast check: Ensure CTA labels and form fields meet WCAG AA contrast ratio standards.
   - Text wrap: CTA labels must fit on a single line at desktop width.
   - Shape consistency: Use a consistent corner-radius scale across components.
