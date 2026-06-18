from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TargetWindowConfig:
    title_keyword: str = 'Pokémon Champions'
    process_name: str = ''
    last_hwnd: int | None = None
    last_title: str = ''

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'TargetWindowConfig':
        return cls(
            title_keyword=data.get('title_keyword') or 'Pokémon Champions',
            process_name=data.get('process_name') or '',
            last_hwnd=data.get('last_hwnd'),
            last_title=data.get('last_title') or '',
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'title_keyword': self.title_keyword,
            'process_name': self.process_name,
            'last_hwnd': self.last_hwnd,
            'last_title': self.last_title,
        }


def load_target_window(path: str | Path) -> TargetWindowConfig:
    p = Path(path)
    if not p.exists():
        return TargetWindowConfig()
    return TargetWindowConfig.from_dict(json.loads(p.read_text(encoding='utf-8')))


def save_target_window(path: str | Path, config: TargetWindowConfig) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(config.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
