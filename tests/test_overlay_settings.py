from app.state.overlay_settings import OverlaySettings, load_overlay_settings, save_overlay_settings


def test_overlay_settings_roundtrip(tmp_path):
    path = tmp_path / 'overlay_settings.json'
    settings = OverlaySettings(opacity=0.75, compact_mode=False, lock_position=True, width=420)
    save_overlay_settings(path, settings)
    loaded = load_overlay_settings(path)
    assert loaded.opacity == 0.75
    assert loaded.compact_mode is False
    assert loaded.lock_position is True
    assert loaded.width == 420
