## Summary

<!-- What does this change do, and why? Link any related issue(s). -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactor / internal change (no behavior change)
- [ ] CI / tooling

## Checklist

These mirror the real gates in `.github/workflows/qa.yml` and `.github/workflows/e2e.yml` — please run what's relevant locally before requesting review:

- [ ] Backend: `ruff check .` and `ruff format --check .` pass
- [ ] Backend: `pytest --cov=src --cov-report=term-missing --cov-fail-under=80` passes (coverage floor is 80%, overall and per major module)
- [ ] Frontend: `pnpm lint` and `pnpm build` pass (from `src/frontend`)
- [ ] Frontend: `pnpm coverage` passes the coverage gate
- [ ] E2E: `pnpm exec playwright test` passes, if this PR touches frontend behavior
- [ ] Added/updated an Alembic migration, if this PR changes a SQLAlchemy model
- [ ] Tests only touch isolated/temp DB and vector-store paths — never the real `chatbot.db` or the real vector store directory
- [ ] Updated relevant docs under `docs/` and/or `CLAUDE.md`, if this PR changes architecture or an invariant documented there

## Notes for the reviewer

<!-- Anything non-obvious: trade-offs made, things intentionally left out, follow-up work. -->
