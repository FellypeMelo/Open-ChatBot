# Gemini Instructions & Corrections Log

## Essential Rules & Preferences
1. **Package Manager**: ALWAYS use `pnpm` (never `npm` or `yarn`) for all frontend operations, dependencies, and script runs (e.g., `pnpm test`, `pnpm dev`, `pnpm install`).
2. **Environment & Shell**: Running on Windows (win32) using PowerShell. Always write PowerShell-compatible command syntax (e.g., `Remove-Item` instead of `rm`, `New-Item` instead of `touch`).
3. **Database & Migration Rules**: 
   - **Never** access the production database (`chatbot.db`) during testing. Ensure tests create a temporary, clean, and fully reset environment for every run.
   - **Always** write manual SQLite `ALTER TABLE` migrations inside `src/backend/db/database.py:init_db()` whenever modifying SQLAlchemy models. Relying purely on `Base.metadata.create_all()` is forbidden as it ignores existing tables.
4. **Test Coverage**: Maintain at least 80% test coverage for both frontend and backend codebases (overall and per major module/file). Ensure new features include corresponding tests.
5. **Design Taste & Mobile Responsiveness**: Follow high-end anti-slop visual standards. Keep hero sections within viewport using `min-h-[100dvh]` instead of `h-screen`. Prefer CSS Grid over flexbox math (`grid grid-cols-...`). Ensure mobile navigation menu is clean, responsive, and collapses gracefully on screens `< 768px` (using sidebar drawer or modal hamburger patterns).
6. **Testing Mandate**: Always require End-to-End (E2E) tests when making database or architectural changes to ensure DB migrations and complex integrations actually work outside of isolated TDD unit test environments.
7. **Always Plan First**: Before executing large changes, creating new files (like tests or features), or running complex terminal commands, you must explicitly outline your plan to the user. Do not execute blindly. Present the strategy, explain what files will be modified, and wait for implicit or explicit alignment.

## Project Context
We are working on **Open-ChatBot**, a stateful, modular AI character platform.
- **Backend**: Python (FastAPI/pytest). Uses `llama-server.exe` for model inference and embeddings (configured in `models_config.json`).
- **Frontend**: React + TypeScript + Vite + TailwindCSS.
- **Last Status**: Shipped the E.P.I.C. RP overhaul — E.P.I.C. master prompt + dual-position recency anchor, per-turn scene extractor, `dynamic_persona` static/dynamic toggle, card-cap removal + sentence-boundary truncation, 48k context + history-window cap, warmth-dial `compress_state`. Adversarially reviewed (ultracode) and hardened. See `CLAUDE.md` and `docs/en/architecture.md` for the current architecture.

## Corrections Log
| 2026-06-22 | User Correction | Tried using `npm run test` instead of `pnpm`. | Under-specified initial package manager preference. Resolved: Always use `pnpm` in this workspace. |
| 2026-06-30 | Missing DB Schema | 500 Errors caused by missing SQLite columns due to lack of migrations. TDD missed it. | Always enforce E2E testing for DB changes and explicitly write manual `ALTER TABLE` migrations in `database.py`. Ensure tests run in a clean, reset environment. |
| 2026-06-30 | "Always plan first" | Added rule mandating that the agent must outline its strategy and planned file/command actions before executing them. |

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