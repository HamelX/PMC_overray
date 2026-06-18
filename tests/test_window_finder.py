from app.capture.window_finder import WindowInfo, filter_windows, window_to_mss_region


def test_filter_windows_by_title_and_process():
    windows = [
        WindowInfo(1, 'Pokémon Champions', 10, 'Champions.exe', (10, 20, 810, 620)),
        WindowInfo(2, 'Browser', 20, 'chrome.exe', (0, 0, 100, 100)),
    ]
    assert filter_windows(windows, title_keyword='champions')[0].hwnd == 1
    assert filter_windows(windows, process_name='champions.exe')[0].hwnd == 1
    assert filter_windows(windows, title_keyword='missing') == []


def test_window_to_mss_region_from_rect():
    window = WindowInfo(1, 'Game', 10, 'game.exe', (10, 20, 810, 620))
    assert window_to_mss_region(window) == {'left': 10, 'top': 20, 'width': 800, 'height': 600}
