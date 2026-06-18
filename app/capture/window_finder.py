from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class WindowInfo:
    """캡처 대상 후보 창 정보.

    프로세스 메모리나 내부 데이터가 아니라 Windows가 공개하는 창 제목/위치/PID만 사용한다.
    """

    hwnd: int
    title: str
    pid: int | None = None
    process_name: str = ""
    rect: tuple[int, int, int, int] = (0, 0, 0, 0)

    @property
    def width(self) -> int:
        return max(0, self.rect[2] - self.rect[0])

    @property
    def height(self) -> int:
        return max(0, self.rect[3] - self.rect[1])


def _process_name(pid: int | None) -> str:
    if not pid:
        return ""
    try:
        import psutil

        return psutil.Process(pid).name()
    except Exception:
        return ""


def list_windows() -> list[WindowInfo]:
    """현재 보이는 최상위 Windows 창 목록을 반환한다.

    pywin32가 없는 Linux/macOS/CI 환경에서는 빈 목록을 반환한다.
    """

    try:
        import win32gui
        import win32process
    except Exception:
        return []

    windows: list[WindowInfo] = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd).strip()
        if not title:
            return
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        if right <= left or bottom <= top:
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        windows.append(
            WindowInfo(
                hwnd=int(hwnd),
                title=title,
                pid=int(pid) if pid else None,
                process_name=_process_name(pid),
                rect=(int(left), int(top), int(right), int(bottom)),
            )
        )

    win32gui.EnumWindows(callback, None)
    return windows


def filter_windows(
    windows: Iterable[WindowInfo],
    title_keyword: str = "",
    process_name: str = "",
) -> list[WindowInfo]:
    """창 제목 또는 프로세스명으로 캡처 후보를 필터링한다."""

    title_q = title_keyword.casefold().strip()
    proc_q = process_name.casefold().strip()
    result: list[WindowInfo] = []
    for window in windows:
        if title_q and title_q not in window.title.casefold():
            continue
        if proc_q and proc_q not in window.process_name.casefold():
            continue
        result.append(window)
    return sorted(result, key=lambda w: (w.title.casefold(), w.hwnd))


def find_window(title_keyword: str = "", process_name: str = "") -> WindowInfo | None:
    """조건에 맞는 첫 번째 창을 찾는다."""

    matches = filter_windows(list_windows(), title_keyword, process_name)
    return matches[0] if matches else None


def window_to_mss_region(window: WindowInfo, client_area_only: bool = False) -> dict[str, int]:
    """mss.grab()에 넘길 수 있는 영역 dict로 변환한다.

    client_area_only는 pywin32가 있을 때 테두리/타이틀바를 제외한 클라이언트 영역을 시도한다.
    실패하면 전체 창 rect를 사용한다.
    """

    if client_area_only:
        try:
            import win32gui

            left, top = win32gui.ClientToScreen(window.hwnd, (0, 0))
            right, bottom = win32gui.ClientToScreen(
                window.hwnd,
                (
                    win32gui.GetClientRect(window.hwnd)[2],
                    win32gui.GetClientRect(window.hwnd)[3],
                ),
            )
            if right > left and bottom > top:
                return {"left": left, "top": top, "width": right - left, "height": bottom - top}
        except Exception:
            pass

    left, top, right, bottom = window.rect
    return {"left": left, "top": top, "width": max(0, right - left), "height": max(0, bottom - top)}
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
