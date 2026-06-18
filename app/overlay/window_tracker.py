from __future__ import annotations

from dataclasses import dataclass

from app.capture.window_finder import WindowInfo, find_window


@dataclass
class TrackedWindow:
    title_keyword: str
    window: WindowInfo | None = None

    def refind(self) -> WindowInfo | None:
        self.window = find_window(title_keyword=self.title_keyword)
        return self.window

    def overlay_position(self) -> tuple[int, int]:
        if not self.window:
            return (40, 80)
        left, top, _, _ = self.window.rect
        return (left + 24, top + 72)
