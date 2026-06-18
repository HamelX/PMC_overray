from __future__ import annotations

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget


def bind_hotkeys(
    widget: QWidget,
    *,
    toggle_visible,
    toggle_click_through,
    reload_state,
    refind_window,
    quit_demo,
    scan_ability=None,
    scan_status=None,
    confirm_pending=None,
) -> None:
    if scan_ability:
        QShortcut(QKeySequence('F6'), widget, activated=scan_ability)
    if scan_status:
        QShortcut(QKeySequence('F7'), widget, activated=scan_status)
    QShortcut(QKeySequence('F8'), widget, activated=toggle_visible)
    QShortcut(QKeySequence('F9'), widget, activated=toggle_click_through)
    QShortcut(QKeySequence('F10'), widget, activated=reload_state)
    QShortcut(QKeySequence('F11'), widget, activated=refind_window)
    if confirm_pending:
        QShortcut(QKeySequence('F12'), widget, activated=confirm_pending)
    QShortcut(QKeySequence('Esc'), widget, activated=quit_demo)
