"""Tests for scripts/reprocess_avatars.py -- the manual, one-off migration
that backfills the downscale/EXIF-correction/format logic already applied
to *new* avatar uploads (_save_avatar_image in
src/backend/api/characters.py) onto avatars that were already sitting on
disk before that logic existed.

Everything here operates on an isolated tmp_path directory standing in for
static/avatars/ -- never the real one -- per this repo's test-isolation
rule (CLAUDE.md). The script's own module-level main()/CLI entrypoint is
intentionally not invoked as a subprocess; reprocess_all() and
reprocess_avatar_file() are imported directly and exercised as plain
functions, exactly as the script itself calls them.
"""

from io import BytesIO
from pathlib import Path

from PIL import Image

from scripts.reprocess_avatars import (
    reprocess_all,
    reprocess_avatar_file,
    _looks_like_avatar_file,
)
from src.backend.api.characters import AVATAR_MAX_DIMENSION


def _png_bytes(width: int, height: int) -> bytes:
    buf = BytesIO()
    Image.new("RGB", (width, height), color=(120, 40, 200)).save(buf, format="PNG")
    return buf.getvalue()


def test_reprocess_avatar_file_downscales_oversized_avatar(tmp_path):
    """A legacy full-resolution avatar already on disk gets downscaled to
    fit AVATAR_MAX_DIMENSION when run through the script's core
    per-file function directly."""
    src_width, src_height = 2000, 1200  # well above AVATAR_MAX_DIMENSION
    avatar_path = tmp_path / "1.png"
    avatar_path.write_bytes(_png_bytes(src_width, src_height))

    result = reprocess_avatar_file(avatar_path)

    assert result == "processed"
    with Image.open(avatar_path) as saved:
        saved_width, saved_height = saved.size
    assert max(saved_width, saved_height) <= AVATAR_MAX_DIMENSION
    assert saved_width < src_width
    assert saved_height < src_height


def test_reprocess_avatar_file_leaves_small_avatar_unchanged(tmp_path):
    """An avatar already at/under AVATAR_MAX_DIMENSION is a no-op: the
    script's pre-check skips rewriting it, and its dimensions are
    reported unchanged (this is also what makes a second run over an
    already-migrated directory idempotent)."""
    src_width, src_height = 50, 30
    avatar_path = tmp_path / "2.png"
    original_bytes = _png_bytes(src_width, src_height)
    avatar_path.write_bytes(original_bytes)

    result = reprocess_avatar_file(avatar_path)

    assert result == "skipped"
    with Image.open(avatar_path) as saved:
        assert saved.size == (src_width, src_height)
    # Untouched entirely -- not just same-dimensions, but byte-identical,
    # since the pre-check skips the write outright.
    assert avatar_path.read_bytes() == original_bytes


def test_reprocess_all_processes_and_skips_across_a_directory(tmp_path):
    """End-to-end over a directory standing in for static/avatars/: one
    oversized avatar gets processed, one already-small avatar is
    skipped, and a non-avatar file (e.g. a stray .gitkeep) is skipped
    without being touched or mistaken for a broken avatar."""
    big = tmp_path / "10.png"
    big.write_bytes(_png_bytes(1600, 900))

    small = tmp_path / "11.png"
    small.write_bytes(_png_bytes(64, 64))

    not_an_avatar = tmp_path / ".gitkeep"
    not_an_avatar.write_text("")

    summary = reprocess_all(tmp_path)

    assert summary.processed == 1
    assert summary.skipped == 2  # small avatar + .gitkeep
    assert summary.errored == 0
    assert summary.errors == []

    with Image.open(big) as saved:
        assert max(saved.size) <= AVATAR_MAX_DIMENSION
    with Image.open(small) as saved:
        assert saved.size == (64, 64)
    assert not_an_avatar.exists()


def test_reprocess_all_continues_past_a_per_file_error(tmp_path, monkeypatch):
    """One file failing to reprocess must not abort the run -- later
    files still get processed, and the failure is counted and logged
    rather than raised."""
    broken = tmp_path / "20.png"
    broken.write_bytes(_png_bytes(1600, 900))

    healthy = tmp_path / "21.png"
    healthy.write_bytes(_png_bytes(1600, 900))

    import scripts.reprocess_avatars as reprocess_avatars_module

    original = reprocess_avatars_module.reprocess_avatar_file

    def _boom_on_first_file(path: Path) -> str:
        if path.name == "20.png":
            raise RuntimeError("simulated failure")
        return original(path)

    monkeypatch.setattr(
        reprocess_avatars_module, "reprocess_avatar_file", _boom_on_first_file
    )

    summary = reprocess_all(tmp_path)

    assert summary.errored == 1
    assert summary.errors == [("20.png", "simulated failure")]
    assert summary.processed == 1  # healthy.png still got processed

    with Image.open(healthy) as saved:
        assert max(saved.size) <= AVATAR_MAX_DIMENSION


def test_reprocess_all_on_missing_directory_is_a_safe_no_op(tmp_path):
    """Pointing the script at a directory that doesn't exist (e.g. a
    fresh checkout with no avatars uploaded yet) must not raise."""
    missing_dir = tmp_path / "does-not-exist"

    summary = reprocess_all(missing_dir)

    assert summary.processed == 0
    assert summary.skipped == 0
    assert summary.errored == 0


def test_looks_like_avatar_file_filters_by_png_suffix(tmp_path):
    """Only regular .png files are treated as avatars -- matching how
    _save_avatar_image always writes to a `<id>.png` path regardless of
    the uploaded source format."""
    png_file = tmp_path / "5.png"
    png_file.write_bytes(_png_bytes(10, 10))
    assert _looks_like_avatar_file(png_file) is True

    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("not an avatar")
    assert _looks_like_avatar_file(txt_file) is False

    subdir = tmp_path / "subdir.png"
    subdir.mkdir()
    assert _looks_like_avatar_file(subdir) is False
