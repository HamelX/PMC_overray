def list_windows():
    """Windows에서는 pywin32로 창 목록을 반환한다. 비-Windows/미설치 환경은 빈 목록."""
    try:
        import win32gui
    except Exception:
        return []
    wins=[]
    def cb(hwnd, _):
        title=win32gui.GetWindowText(hwnd)
        if title and win32gui.IsWindowVisible(hwnd): wins.append({'hwnd':hwnd,'title':title})
    win32gui.EnumWindows(cb, None)
    return wins
