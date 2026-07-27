# Security Policy

## Reporting a vulnerability

Please **do not open a public GitHub issue** for a security vulnerability.

Use GitHub's private vulnerability reporting instead: go to the **Security** tab of this repository → **Report a vulnerability**, which opens a private [GitHub Security Advisory](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) thread with the maintainer. This keeps the report private until a fix is available.

If the "Report a vulnerability" option isn't visible (private reporting is a per-repository setting the maintainer must enable), open a normal issue asking for it to be enabled — without including any vulnerability details there.

## Supported versions

There are no tagged releases yet (see [CHANGELOG.md](CHANGELOG.md)); the only supported version is the latest commit on `main`. Fixes land there, not on older commits.

## Scope: what this application actually is

Open-ChatBot is a **local-first, single-tenant application**. Understanding its real security model matters for judging what counts as a valid report:

* **No authentication middleware.** API endpoints (`/chat`, `/characters`, `/settings`, etc.) do not enforce any login, session, or token check. The backend auto-provisions a single local user.
* **Binds to `127.0.0.1` by default.** `run.sh` / `run.bat` also expose an explicit **LAN mode** (binding `0.0.0.0`) for reaching the app from a phone/tablet on the same Wi-Fi. Both scripts print an on-screen warning when LAN mode is active: *"The app has NO login: anyone on this network can use it."* LAN mode is opt-in and is not the default.
* **Persistence is entirely local**: a SQLite file (`chatbot.db`) and a local vector-store directory. There is no network-facing datastore, and no data leaves the machine except to the local `llama-server` subprocess.
* **No secrets ship in the repository.** `.env.example` and `models_config.example.json` are templates; real config (`.env`, `models_config.json`) is gitignored and expected to point at a model file and binary the user supplies themselves.

Given this scope, reports that are genuinely in scope include, for example: a request that lets a client on the same machine or LAN do something a same-origin browser tab from the app itself could not already do; path traversal in any file-handling endpoint; SSRF against the local `llama-server` subprocess from outside the intended flow; SQL injection; or any way one character's/chat's data becomes reachable from another scope it shouldn't be (see the per-`(character_id, chat_id)` isolation invariants documented in [CLAUDE.md](CLAUDE.md)).

"There is no authentication" is a known, documented property of the current single-user design (see [docs/en/api/auth.md](docs/en/api/auth.md) and [docs/en/architecture/security.md](docs/en/architecture/security.md)), not itself a novel finding — but concrete exploitation paths building on it (e.g. from an untrusted page in the same browser, or from another device on a LAN-mode network) are still useful reports.

## Dependencies

Backend dependencies are pinned in `requirements.txt` / `requirements-lock.txt`; frontend dependencies are pinned via `src/frontend/pnpm-lock.yaml`. If you find a vulnerable pinned version, a report through the channel above (or a plain PR bumping the pin, for a clearly non-sensitive case) is welcome.
