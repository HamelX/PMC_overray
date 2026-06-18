from __future__ import annotations

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget


def bind_hotkeys(widget: QWidget, *, toggle_visible, toggle_click_through, reload_state, refind_window, quit_demo) -> None:
    QShortcut(QKeySequence('F8'), widget, activated=toggle_visible)
    QShortcut(QKeySequence('F9'), widget, activated=toggle_click_through)
    QShortcut(QKeySequence('F10'), widget, activated=reload_state)
    QShortcut(QKeySequence('F11'), widget, activated=refind_window)
    QShortcut(QKeySequence('Esc'), widget, activated=quit_demo)
