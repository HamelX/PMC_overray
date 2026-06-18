from app.capture.window_finder import WindowInfo
from app.overlay.window_labels import window_label
from app.overlay.window_tracker import TrackedWindow
from app.state.target_window import TargetWindowConfig, load_target_window, save_target_window


def test_target_window_config_roundtrip(tmp_path):
    path = tmp_path / 'target_window.json'
    config = TargetWindowConfig('LDPlayer', 'dnplayer.exe', 123, 'LDPlayer - Pokémon Champions')
    save_target_window(path, config)
    loaded = load_target_window(path)
    assert loaded.process_name == 'dnplayer.exe'
    assert loaded.last_hwnd == 123


def test_tracked_window_can_use_selected_process_window():
    window = WindowInfo(10, 'LDPlayer - Pokémon Champions', 100, 'dnplayer.exe', (10, 20, 810, 620))
    tracker = TrackedWindow('Pokémon Champions')
    tracker.set_selected(window)
    assert tracker.title_keyword == window.title
    assert tracker.process_name == 'dnplayer.exe'
    assert tracker.overlay_position() == (34, 92)
    assert 'dnplayer.exe' in window_label(window)
