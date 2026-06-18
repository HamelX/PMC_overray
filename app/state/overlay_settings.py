from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class OverlaySettings:
    opacity: float = 0.88
    compact_mode: bool = True
    lock_position: bool = False
    width: int = 360

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'OverlaySettings':
        return cls(
            opacity=float(data.get('opacity', 0.88)),
            compact_mode=bool(data.get('compact_mode', True)),
            lock_position=bool(data.get('lock_position', False)),
            width=int(data.get('width', 360)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'opacity': self.opacity,
            'compact_mode': self.compact_mode,
            'lock_position': self.lock_position,
            'width': self.width,
        }


def load_overlay_settings(path: str | Path) -> OverlaySettings:
    p = Path(path)
    if not p.exists():
        return OverlaySettings()
    return OverlaySettings.from_dict(json.loads(p.read_text(encoding='utf-8')))


def save_overlay_settings(path: str | Path, settings: OverlaySettings) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(settings.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
