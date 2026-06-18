from __future__ import annotations

from dataclasses import dataclass

from app.capture.window_finder import WindowInfo, find_window


@dataclass
class TrackedWindow:
    title_keyword: str
    process_name: str = ''
    window: WindowInfo | None = None

    def refind(self) -> WindowInfo | None:
        self.window = find_window(title_keyword=self.title_keyword, process_name=self.process_name)
        return self.window

    def set_selected(self, window: WindowInfo) -> None:
        self.window = window
        self.title_keyword = window.title
        self.process_name = window.process_name

    def overlay_position(self) -> tuple[int, int]:
        if not self.window:
            return (40, 80)
        left, top, _, _ = self.window.rect
        return (left + 24, top + 72)
