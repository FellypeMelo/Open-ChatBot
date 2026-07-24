#!/usr/bin/env python3
"""One-off migration: reprocess every avatar already sitting on disk
through the same downscale / EXIF-orientation-correction / format logic
new uploads get (see `_save_avatar_image` in
src/backend/api/characters.py).

Why this exists
----------------
Server-side avatar downscaling (max AVATAR_MAX_DIMENSION px, EXIF
orientation baked in, re-encoded as optimized PNG) was added on the
*upload* path only. That only benefits avatars uploaded from now on --
avatars already on disk from before that change are untouched: still
full-resolution originals (up to 5MB), possibly sideways/upside down if
they came from a phone camera. This script backfills those by running
each existing file through the exact same `_save_avatar_image()`
function new uploads use, imported (not reimplemented) from
characters.py, so behavior is guaranteed identical.

This is a manual, developer-run script ONLY. It is intentionally NOT
wired into app startup, a request handler, a lifespan hook, or any
other automatic trigger -- consistent with this repo's own conservative
migration philosophy (CLAUDE.md: schema migrations are managed by
Alembic and are "never run ... automatically against the real DB --
the user runs `alembic upgrade head`"). The same rule applies here: a
human must run it explicitly, from the repo root:

    venv/Scripts/python.exe scripts/reprocess_avatars.py

Idempotency
-----------
`_save_avatar_image()` is already idempotent on *dimensions* --
`Image.thumbnail()` is documented as a no-op once the image already
fits within the target box -- but calling it unconditionally on every
run would still re-decode and re-encode (and rewrite to disk) every
avatar file every single time, even ones that need no change at all.

This script adds an explicit pre-check instead: it reads each avatar's
current pixel size before touching it, and skips the write entirely
when the avatar already fits within AVATAR_MAX_DIMENSION. We chose the
pre-check over the simpler "always call _save_avatar_image"
unconditionally because:

  * it keeps the summary's "skipped/already-small" count meaningful --
    re-running over an already-migrated avatars/ directory reports
    "0 processed" instead of "N processed" for files nothing actually
    changed on;
  * it avoids a pointless decode/re-encode/disk-write cycle for files
    that need no work.

The pre-check only inspects raw pixel dimensions, not EXIF orientation.
That is not a gap in practice: a legacy avatar that still carries an
un-baked EXIF orientation tag is, by construction, an unprocessed
phone-camera photo, and phone-camera photos are always far larger than
AVATAR_MAX_DIMENSION (512px) on their long side straight off the
sensor -- so any avatar that actually needs EXIF correction will also
fail the dimension check and go through full reprocessing (resize +
EXIF-bake + re-encode) anyway. A small, already-optimized avatar with a
leftover bad orientation tag is not a state any current code path
(upload or this script) can produce.

Errors on individual files (corrupt file, permission error, etc.) are
caught, logged, and counted -- they never abort the run.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# This script lives in scripts/, not the repo root, so when it's invoked
# directly (`python scripts/reprocess_avatars.py`) sys.path[0] is scripts/,
# not the repo root -- `import src...` would fail without this. Inserted
# before the src import below on purpose.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.api.characters import (  # noqa: E402
    _save_avatar_image,
    AVATAR_MAX_DIMENSION,
)

AVATARS_DIR = PROJECT_ROOT / "static" / "avatars"


@dataclass
class ReprocessSummary:
    """Tally of a reprocess_all() run, for the printed summary and for
    tests to assert against without scraping stdout."""

    processed: int = 0
    skipped: int = 0
    errored: int = 0
    errors: list[tuple[str, str]] = field(default_factory=list)


def _looks_like_avatar_file(path: Path) -> bool:
    """True if `path` looks like a file _save_avatar_image() could have
    written. Every avatar is saved to a `<character_id>.png` path --
    both the resize success path and its raw-bytes fallback (for
    undecodable uploads) write to that same `.png`-suffixed path -- so
    anything else sitting in static/avatars/ (a stray .gitkeep,
    Thumbs.db, a subdirectory, ...) is not an avatar and must be left
    alone rather than blindly reprocessed."""
    return path.is_file() and path.suffix.lower() == ".png"


def reprocess_avatar_file(path: Path) -> str:
    """Reprocess a single avatar file in place, through the exact same
    _save_avatar_image() logic new uploads get.

    Returns "processed" if the file was rewritten, or "skipped" if it
    was already within AVATAR_MAX_DIMENSION and left untouched (see the
    idempotency note in the module docstring).

    Raises on failure -- callers are responsible for catching per-file
    errors so one bad file doesn't abort the whole run (see
    reprocess_all()).
    """
    from PIL import Image

    try:
        with Image.open(path) as img:
            width, height = img.size
        if max(width, height) <= AVATAR_MAX_DIMENSION:
            return "skipped"
    except Exception:
        # Not decodable as an image by this pre-check -- fall through and
        # let _save_avatar_image() handle it exactly as it would for a
        # fresh upload (it has its own raw-bytes fallback for this case).
        pass

    content = path.read_bytes()
    _save_avatar_image(str(path), content)
    return "processed"


def reprocess_all(avatars_dir: Path) -> ReprocessSummary:
    """Walk every entry in `avatars_dir`, reprocess each one that looks
    like an avatar file, and return a summary. Never raises for a
    per-file failure -- those are caught, logged, and counted so the run
    continues past them."""
    summary = ReprocessSummary()

    if not avatars_dir.exists():
        print(f"Avatars directory not found at {avatars_dir}, nothing to do.")
        return summary

    for entry in sorted(avatars_dir.iterdir()):
        if not _looks_like_avatar_file(entry):
            summary.skipped += 1
            continue

        try:
            result = reprocess_avatar_file(entry)
        except Exception as exc:
            summary.errored += 1
            summary.errors.append((entry.name, str(exc)))
            print(f"  ERROR reprocessing {entry.name}: {exc}")
            continue

        if result == "processed":
            summary.processed += 1
            print(f"  Reprocessed {entry.name}")
        else:
            summary.skipped += 1

    return summary


def main() -> None:
    print("Open-ChatBot Avatar Reprocessing")
    print("=" * 40)
    print(f"Scanning {AVATARS_DIR} ...")
    summary = reprocess_all(AVATARS_DIR)
    print("=" * 40)
    print(
        f"Done. {summary.processed} processed, "
        f"{summary.skipped} skipped/already-small, "
        f"{summary.errored} errored."
    )
    if summary.errors:
        print("Errors:")
        for name, reason in summary.errors:
            print(f"  {name}: {reason}")


if __name__ == "__main__":
    main()
