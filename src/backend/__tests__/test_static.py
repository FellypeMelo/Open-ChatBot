from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from fastapi.responses import PlainTextResponse

from src.backend.main import app, _PWA_RUNTIME_FILENAME_RE

client = TestClient(app)


def test_get_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_index_html_catch_all_is_never_cached():
    # index.html is the ONE file in the SPA build that is never
    # content-hashed. A rebuild changes every /assets/* filename, so a
    # cached stale index.html would keep requesting asset URLs that no
    # longer exist -- this header is what prevents that class of bug.
    response = client.get("/some/nonexistent/spa/route")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store, must-revalidate"


def test_assets_mount_is_cached_immutably():
    # static/assets is Vite's real, content-hashed build output directory.
    # Write a throwaway probe file into it (and clean up after) rather than
    # depending on whatever a previous local build happens to have produced.
    assets_dir = Path("static/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    probe = assets_dir / "__cache_header_probe__.txt"
    probe.write_text("probe")
    try:
        response = client.get("/assets/__cache_header_probe__.txt")
        assert response.status_code == 200
        assert (
            response.headers["cache-control"] == "public, max-age=31536000, immutable"
        )
    finally:
        probe.unlink(missing_ok=True)


def test_avatars_mount_is_not_marked_immutable():
    # Avatars are user-uploaded/mutable (re-uploading a character's avatar
    # reuses the same URL), unlike the content-hashed /assets bundle -- they
    # must NOT get the immutable long-lived Cache-Control treatment.
    avatars_dir = Path("static/avatars")
    avatars_dir.mkdir(parents=True, exist_ok=True)
    probe = avatars_dir / "__cache_header_probe__.txt"
    probe.write_text("probe")
    try:
        response = client.get("/avatars/__cache_header_probe__.txt")
        assert response.status_code == 200
        assert (
            response.headers.get("cache-control")
            != "public, max-age=31536000, immutable"
        )
    finally:
        probe.unlink(missing_ok=True)


def test_manifest_webmanifest_served_with_correct_media_type(monkeypatch):
    mock_file_response = MagicMock(return_value=PlainTextResponse("{}"))
    monkeypatch.setattr("src.backend.main.FileResponse", mock_file_response)

    response = client.get("/manifest.webmanifest")

    assert response.status_code == 200
    mock_file_response.assert_any_call(
        "static/manifest.webmanifest", media_type="application/manifest+json"
    )


def test_static_routes(monkeypatch):
    # Test favicon and catch-all frontend routes. FileResponse is mocked
    # with a real lightweight Response (rather than a bare string) so the
    # endpoint's own `response.headers[...] = ...` mutation still behaves
    # like it would against a real FileResponse/Response instance.
    def fake_file_response(*args, **kwargs):
        return PlainTextResponse("FileResponseMock")

    mock_file_response = MagicMock(side_effect=fake_file_response)
    monkeypatch.setattr("src.backend.main.FileResponse", mock_file_response)

    client_local = TestClient(app)

    # Favicon endpoint
    resp = client_local.get("/favicon.svg")
    assert resp.status_code == 200
    mock_file_response.assert_any_call("static/favicon.svg")

    # Catch-all frontend route
    resp = client_local.get("/some/random/route")
    assert resp.status_code == 200
    mock_file_response.assert_any_call("static/index.html")


def test_pwa_runtime_filename_regex_matches_expected_names():
    # sw.js and its hashed Workbox runtime chunk (vite-plugin-pwa's
    # generateSW output) must match; anything merely similar must not.
    assert _PWA_RUNTIME_FILENAME_RE.match("sw.js")
    assert _PWA_RUNTIME_FILENAME_RE.match("workbox-98f7a950.js")
    assert _PWA_RUNTIME_FILENAME_RE.match("workbox-AbC-123_xyz.js")
    assert not _PWA_RUNTIME_FILENAME_RE.match("sw.js.map")
    assert not _PWA_RUNTIME_FILENAME_RE.match("workbox-98f7a950.js.map")
    assert not _PWA_RUNTIME_FILENAME_RE.match("nested/sw.js")
    assert not _PWA_RUNTIME_FILENAME_RE.match("random.js")


def test_pwa_runtime_file_served_as_javascript_not_index_html():
    # Exercises the real catch-all branch end-to-end without touching a
    # real static/sw.js that may or may not exist locally: any filename
    # matching the shared regex takes the same code path, so a uniquely
    # named workbox-*.js probe proves the sw.js case too.
    probe = Path("static/workbox-__test_probe__.js")
    probe.write_text("// workbox runtime probe")
    try:
        response = client.get("/workbox-__test_probe__.js")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/javascript")
        assert response.headers["cache-control"] == "no-cache"
        assert response.text == "// workbox runtime probe"
    finally:
        probe.unlink(missing_ok=True)


def test_pwa_runtime_lookalike_missing_from_disk_falls_back_to_index_html():
    # A matching filename that doesn't actually exist on disk must fall
    # through to the normal SPA index.html response, not 404.
    response = client.get("/workbox-__definitely_missing__.js")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert response.headers["cache-control"] == "no-store, must-revalidate"
