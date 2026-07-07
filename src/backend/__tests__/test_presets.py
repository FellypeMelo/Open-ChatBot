from src.backend.db.models import SamplerPreset


def test_create_preset_defaults(client, db_session):
    # POST /presets/ with only the required "name" field -- everything else
    # should fall back to PresetCreateSchema's defaults.
    response = client.post("/presets/", json={"name": "Balanced"})
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Balanced"
    assert data["is_default"] is False
    assert data["temperature"] == 1.0
    assert data["min_p"] == 0.05
    assert data["top_k"] == 0
    assert data["top_p"] == 1.0
    assert data["repeat_penalty"] == 1.0
    assert data["dry_multiplier"] == 0.0
    assert data["dry_base"] == 1.75
    assert data["dry_range"] == 2048
    assert data["xtc_threshold"] == 0.0
    assert data["xtc_probability"] == 0.0

    # Persisted for real, not just echoed back.
    preset = db_session.query(SamplerPreset).filter_by(name="Balanced").first()
    assert preset is not None
    assert preset.is_default is False


def test_create_preset_with_is_default_clears_previous_default(client, db_session):
    # First preset created as the default.
    first = client.post("/presets/", json={"name": "Preset A", "is_default": True})
    assert first.status_code == 200
    assert first.json()["is_default"] is True

    # Creating a second default preset should flip the first one's flag off.
    second = client.post("/presets/", json={"name": "Preset B", "is_default": True})
    assert second.status_code == 200
    assert second.json()["is_default"] is True

    db_session.expire_all()
    preset_a = db_session.query(SamplerPreset).filter_by(name="Preset A").first()
    preset_b = db_session.query(SamplerPreset).filter_by(name="Preset B").first()
    assert preset_a.is_default is False
    assert preset_b.is_default is True


def test_update_preset_changes_fields(client, db_session):
    created = client.post("/presets/", json={"name": "Original", "temperature": 0.5})
    preset_id = created.json()["id"]

    update_payload = {
        "name": "Renamed",
        "temperature": 0.9,
        "top_k": 40,
        "top_p": 0.95,
    }
    response = client.put(f"/presets/{preset_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == preset_id
    assert data["name"] == "Renamed"
    assert data["temperature"] == 0.9
    assert data["top_k"] == 40
    assert data["top_p"] == 0.95
    # Fields not supplied in the payload are left untouched (update_preset uses
    # exclude_unset so a partial PUT can't reset unspecified fields back to
    # PresetCreateSchema's defaults) -- both happen to still equal the
    # schema default here since "Original" was created without customizing them.
    assert data["is_default"] is False
    assert data["min_p"] == 0.05

    db_session.expire_all()
    preset = db_session.query(SamplerPreset).filter_by(id=preset_id).first()
    assert preset.name == "Renamed"
    assert preset.temperature == 0.9


def test_update_preset_with_is_default_reclears_previous_default(client, db_session):
    default_preset = client.post(
        "/presets/", json={"name": "Default One", "is_default": True}
    ).json()
    other_preset = client.post(
        "/presets/", json={"name": "Other", "is_default": False}
    ).json()

    response = client.put(
        f"/presets/{other_preset['id']}",
        json={"name": "Other", "is_default": True},
    )
    assert response.status_code == 200
    assert response.json()["is_default"] is True

    db_session.expire_all()
    refreshed_default = (
        db_session.query(SamplerPreset).filter_by(id=default_preset["id"]).first()
    )
    refreshed_other = (
        db_session.query(SamplerPreset).filter_by(id=other_preset["id"]).first()
    )
    assert refreshed_default.is_default is False
    assert refreshed_other.is_default is True


def test_update_preset_preserves_omitted_customized_fields(client, db_session):
    # Regression test for the exclude_unset fix: a field customized away from
    # its schema default must survive a PUT that doesn't mention it.
    created = client.post("/presets/", json={"name": "Custom", "min_p": 0.2}).json()
    assert created["min_p"] == 0.2

    response = client.put(f"/presets/{created['id']}", json={"name": "Custom Renamed"})
    assert response.status_code == 200
    assert response.json()["min_p"] == 0.2

    db_session.expire_all()
    preset = db_session.query(SamplerPreset).filter_by(id=created["id"]).first()
    assert preset.name == "Custom Renamed"
    assert preset.min_p == 0.2


def test_update_preset_not_found(client):
    response = client.put("/presets/99999", json={"name": "Ghost"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Preset not found"


def test_delete_non_default_preset(client, db_session):
    created = client.post("/presets/", json={"name": "Disposable"}).json()

    response = client.delete(f"/presets/{created['id']}")
    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}

    assert db_session.query(SamplerPreset).filter_by(id=created["id"]).first() is None


def test_delete_default_preset_returns_400(client, db_session):
    created = client.post(
        "/presets/", json={"name": "Protected", "is_default": True}
    ).json()

    response = client.delete(f"/presets/{created['id']}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot delete the default preset"

    # Still present -- the delete must have been rejected before touching the row.
    assert (
        db_session.query(SamplerPreset).filter_by(id=created["id"]).first() is not None
    )


def test_delete_preset_not_found(client):
    response = client.delete("/presets/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Preset not found"
