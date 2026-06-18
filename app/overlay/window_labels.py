from __future__ import annotations

from app.capture.window_finder import WindowInfo


def window_label(window: WindowInfo) -> str:
    size = f'{window.width}x{window.height}'
    proc = window.process_name or 'unknown'
    return f'[{window.pid or "?"}] {proc} · {window.title} · {size}'
