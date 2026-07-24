from io import BytesIO

import pytest
from PIL import Image
from unittest.mock import patch, AsyncMock, MagicMock
from src.backend.db.models import Character
from src.backend.core.orchestration.bridge import Brain
from src.backend.api.characters import AVATAR_MAX_DIMENSION


def _png_bytes(width: int, height: int) -> bytes:
    """Build an in-memory solid-color PNG of the given size for avatar-upload
    resize tests."""
    buf = BytesIO()
    Image.new("RGB", (width, height), color=(120, 40, 200)).save(buf, format="PNG")
    return buf.getvalue()


def _jpeg_bytes_with_orientation(width: int, height: int, orientation: int) -> bytes:
    """Build an in-memory JPEG with the given EXIF Orientation tag (0x0112),
    for avatar-upload EXIF-transpose tests."""
    buf = BytesIO()
    img = Image.new("RGB", (width, height), color=(10, 200, 90))
    exif = img.getexif()
    exif[0x0112] = orientation
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def test_tokenize_endpoint(client):
    with patch(
        "src.backend.core.context.budget.ContextBudgetCalculator.count_tokens",
        new_callable=AsyncMock,
    ) as mock_count:
        mock_count.return_value = 12

        response = client.post("/settings/tokenize", json={"text": "Hello world!"})
        assert response.status_code == 200
        assert response.json() == {"tokens": 12}
        mock_count.assert_called_with("Hello world!")


def test_parse_png_endpoint(client):
    from src.backend.core.importer.png_parser import TavernV2Card, TavernV2Data

    card_data = TavernV2Data(
        name="TavernBot",
        description="A helpful assistant.",
        personality="Helpful and polite.",
        scenario="A cozy workshop.",
        first_mes="Greetings! How can I assist you today?",
        mes_example="user: hi\nbot: hello!",
    )
    mock_card = TavernV2Card(data=card_data)

    with patch(
        "src.backend.core.importer.png_parser.parse_png_character_card",
        return_value=mock_card,
    ):
        response = client.post(
            "/characters/parse-png",
            files={"file": ("bot.png", b"fake-png-data", "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TavernBot"
        assert data["description"] == "A helpful assistant."
        assert data["personality"] == "Helpful and polite."
        assert data["scenario"] == "A cozy workshop."
        assert data["first_mes"] == "Greetings! How can I assist you today?"
        assert data["mes_example"] == "user: hi\nbot: hello!"


def test_create_character_expanded_fields(client, db_session):
    payload = {
        "name": "Kaelen",
        "description": "Short bio description.",
        "nickname": "Kael",
        "short_description": "Bio for sidebar.",
        "persona_prompt": "Quiet and observant.",
        "scenario": "Under a shady oak tree.",
        "first_mes": "What brings you here?",
        "mes_example": "user: hello\nKaele: *nods*",
        "content_rating": "limitless",
    }
    response = client.post("/characters/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Kaelen"
    assert data["nickname"] == "Kael"
    assert data["content_rating"] == "limitless"

    # Verify db state
    char = db_session.query(Character).filter(Character.id == data["id"]).first()
    assert char is not None
    assert char.nickname == "Kael"
    assert char.scenario == "Under a shady oak tree."
    assert char.first_mes == "What brings you here?"
    assert char.mes_example == "user: hello\nKaele: *nods*"
    assert char.content_rating == "limitless"


def test_update_character_expanded_fields(client, db_session):
    char = Character(name="OldName", description="OldDesc")
    db_session.add(char)
    db_session.commit()

    payload = {
        "name": "UpdatedName",
        "description": "UpdatedDesc",
        "nickname": "UpNick",
        "short_description": "UpdatedShort",
        "persona_prompt": "UpdatedPersona",
        "scenario": "UpdatedScenario",
        "first_mes": "UpdatedFirst",
        "mes_example": "UpdatedExample",
        "content_rating": "limitless",
    }
    response = client.put(f"/characters/{char.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "UpNick"

    db_session.refresh(char)
    assert char.nickname == "UpNick"
    assert char.scenario == "UpdatedScenario"
    assert char.first_mes == "UpdatedFirst"
    assert char.mes_example == "UpdatedExample"
    assert char.content_rating == "limitless"


@pytest.mark.asyncio
async def test_prompt_construction_with_expanded_fields():
    mock_vector = MagicMock()
    mock_vector.query_memory = AsyncMock(return_value={"documents": [[]]})
    mock_vector.query_lore = MagicMock()
    mock_vector.query_lore.documents = [[]]
    mock_vector.llm_client = MagicMock()
    mock_vector.llm_client.url = "http://127.0.0.1:8080"

    brain = Brain(vector_store=mock_vector)

    class MockChar:
        id = 10
        name = "Kaelen"
        description = "A standard description."
        short_description = "A custom short bio."
        nickname = "Kael"
        persona_prompt = "Observant and calm."
        scenario = "Resting in a tavern."
        first_mes = "Welcome."
        mes_example = "user: hi\nKael: *looks up*"
        tags = []

    state = {
        "location": "Tavern",
        "mood": "Calm",
        "stats": {
            "energy": 90,
            "hunger": 10,
            "happiness": 80,
            "social": 80,
            "relationship": {"score": 60},
        },
    }

    prompt = await brain.build_prompt("Hello!", MockChar(), state)
    assert "Identity: Kael. A custom short bio." in prompt
    assert "Personality: Observant and calm." in prompt
    assert "Scenario: Resting in a tavern." in prompt
    assert "Example Dialogs:\nuser: hi\nKael: *looks up*" in prompt


def test_upload_avatar_endpoint(client, db_session, monkeypatch, tmp_path):
    """Undecodable "PNG" bytes (no real image data behind the magic number)
    fall back to being written as-is rather than failing the upload -- the
    endpoint never validated image content before the resize step, and that
    behavior is preserved."""
    monkeypatch.chdir(tmp_path)

    char = Character(name="AvatarChar", description="No avatar yet")
    db_session.add(char)
    db_session.commit()

    response = client.post(
        f"/characters/{char.id}/avatar",
        files={"file": ("avatar.png", b"\x89PNG\r\n\x1a\nfake-avatar", "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["avatar_url"] == f"/avatars/{char.id}.png"

    # Verify avatar saved to disk
    avatar_file = tmp_path / "static" / "avatars" / f"{char.id}.png"
    assert avatar_file.exists()


def test_upload_avatar_oversized_image_is_downscaled(
    client, db_session, monkeypatch, tmp_path
):
    """An oversized upload is downscaled to fit within AVATAR_MAX_DIMENSION on
    its longest side, with aspect ratio preserved."""
    monkeypatch.chdir(tmp_path)

    char = Character(name="BigAvatarChar", description="Uploads a huge avatar")
    db_session.add(char)
    db_session.commit()

    src_width, src_height = 2000, 1200  # well above AVATAR_MAX_DIMENSION, 5:3 ratio
    response = client.post(
        f"/characters/{char.id}/avatar",
        files={"file": ("big.png", _png_bytes(src_width, src_height), "image/png")},
    )
    assert response.status_code == 200

    avatar_file = tmp_path / "static" / "avatars" / f"{char.id}.png"
    assert avatar_file.exists()

    with Image.open(avatar_file) as saved:
        saved_width, saved_height = saved.size

    assert max(saved_width, saved_height) <= AVATAR_MAX_DIMENSION
    assert saved_width < src_width
    assert saved_height < src_height
    # Aspect ratio preserved (allow a rounding pixel of slack).
    assert abs(saved_width / saved_height - src_width / src_height) < 0.01


def test_upload_avatar_small_image_is_not_upscaled(
    client, db_session, monkeypatch, tmp_path
):
    """A source image already smaller than AVATAR_MAX_DIMENSION is stored
    unchanged, never enlarged."""
    monkeypatch.chdir(tmp_path)

    char = Character(name="TinyAvatarChar", description="Uploads a tiny avatar")
    db_session.add(char)
    db_session.commit()

    src_width, src_height = 50, 30
    response = client.post(
        f"/characters/{char.id}/avatar",
        files={"file": ("tiny.png", _png_bytes(src_width, src_height), "image/png")},
    )
    assert response.status_code == 200

    avatar_file = tmp_path / "static" / "avatars" / f"{char.id}.png"
    with Image.open(avatar_file) as saved:
        assert saved.size == (src_width, src_height)


def test_upload_avatar_applies_exif_orientation(
    client, db_session, monkeypatch, tmp_path
):
    """A portrait phone photo stored with a non-1 EXIF Orientation tag (the
    common case for camera uploads) must be baked into the pixel data before
    being re-saved as PNG, since PNG has no EXIF-orientation convention and
    nothing downstream would otherwise apply it -- a naive re-save would
    leave every rotated phone photo sideways or upside down."""
    monkeypatch.chdir(tmp_path)

    char = Character(name="RotatedAvatarChar", description="Uploads a rotated avatar")
    db_session.add(char)
    db_session.commit()

    # Orientation 6 = "rotate 90 CW to display correctly": the raw sensor
    # data for a visually-portrait photo is stored landscape (200x100).
    raw_width, raw_height = 200, 100
    response = client.post(
        f"/characters/{char.id}/avatar",
        files={
            "file": (
                "rotated.jpg",
                _jpeg_bytes_with_orientation(raw_width, raw_height, 6),
                "image/jpeg",
            )
        },
    )
    assert response.status_code == 200

    avatar_file = tmp_path / "static" / "avatars" / f"{char.id}.png"
    with Image.open(avatar_file) as saved:
        saved_width, saved_height = saved.size

    # exif_transpose() must correct the orientation before saving, so the
    # stored PNG is visually portrait (taller than wide), not the raw
    # sensor-orientation landscape dimensions.
    assert saved_height > saved_width


def test_upload_avatar_rejects_image_over_pixel_cap(
    client, db_session, monkeypatch, tmp_path
):
    """An image whose declared pixel count exceeds AVATAR_MAX_SOURCE_PIXELS
    is rejected outright (413) rather than being decoded/resized -- and,
    critically, rather than falling through _save_avatar_image's
    undecodable-bytes fallback and being written to disk unresized. The cap
    is monkeypatched low so a cheap, ordinarily-fine-sized PNG exercises the
    same rejection path a genuine decompression-bomb-scale upload would."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("src.backend.api.characters.AVATAR_MAX_SOURCE_PIXELS", 1_000)

    char = Character(name="BombAvatarChar", description="Uploads an oversized avatar")
    db_session.add(char)
    db_session.commit()

    response = client.post(
        f"/characters/{char.id}/avatar",
        files={"file": ("big.png", _png_bytes(64, 64), "image/png")},  # 4096 > 1000
    )

    assert response.status_code == 413
    assert "exceed" in response.json()["detail"]

    avatar_file = tmp_path / "static" / "avatars" / f"{char.id}.png"
    assert not avatar_file.exists()


def test_upload_avatar_rejects_pillow_decompression_bomb(
    client, db_session, monkeypatch, tmp_path
):
    """A genuine PIL.Image.DecompressionBombError raised from inside
    Image.open() (Pillow's own crafted-input guard) must be surfaced as a
    413 and must NOT fall through to _save_avatar_image's broad
    except-fallback, which would otherwise write the still-undecoded
    original bytes to disk unresized -- exactly the input the resize
    feature exists to catch. Pillow's MAX_IMAGE_PIXELS is monkeypatched low
    so an ordinarily-tiny PNG triggers the real DecompressionBombError path
    cheaply, without constructing an actual multi-hundred-megapixel image."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 100)

    char = Character(name="RealBombAvatarChar", description="Uploads a real bomb")
    db_session.add(char)
    db_session.commit()

    # 50x50 = 2500 px > 2 * MAX_IMAGE_PIXELS (200) -> Image.open() itself
    # raises DecompressionBombError.
    response = client.post(
        f"/characters/{char.id}/avatar",
        files={"file": ("bomb.png", _png_bytes(50, 50), "image/png")},
    )

    assert response.status_code == 413

    avatar_file = tmp_path / "static" / "avatars" / f"{char.id}.png"
    assert not avatar_file.exists()


def test_import_png_rejects_image_over_pixel_cap(client, db_session, monkeypatch):
    """The pixel-count guard on the card's embedded image runs before the
    card is parsed and before any Character row is committed, so a
    pathological card is rejected without leaving an orphaned row behind."""
    monkeypatch.setattr("src.backend.api.characters.AVATAR_MAX_SOURCE_PIXELS", 1_000)

    before_count = db_session.query(Character).count()

    response = client.post(
        "/characters/import-png",
        files={"file": ("bomb.png", _png_bytes(64, 64), "image/png")},  # 4096 > 1000
    )

    assert response.status_code == 413
    assert db_session.query(Character).count() == before_count
