from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.config import PENDING_SCAN_FILE


@dataclass
class StatusScanResult:
    pokemon_name: str | None = None
    level: int | None = None
    current_hp: int | None = None
    max_hp: int | None = None
    atk: int | None = None
    def_: int | None = None
    spa: int | None = None
    spd: int | None = None
    spe: int | None = None
    ability: str | None = None
    item: str | None = None
    moves: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    confidence: str = 'failed_or_not_implemented'

    def to_dict(self) -> dict[str, Any]:
        return {
            'pokemon_name': self.pokemon_name,
            'level': self.level,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'atk': self.atk,
            'def': self.def_,
            'spa': self.spa,
            'spd': self.spd,
            'spe': self.spe,
            'ability': self.ability,
            'item': self.item,
            'moves': self.moves,
            'warnings': self.warnings,
            'confidence': self.confidence,
        }


class StatusScreenReader:
    """스테이터스 화면 OCR 연결을 위한 TODO 인터페이스.

    MVP에서는 OCR을 확정 저장하지 않는다. 실패/미구현이면 빈 결과와 경고를 반환하고,
    사용자가 검수할 수 있도록 pending_scan_result.json에만 저장한다.
    """

    def read(self, image_path: str | Path) -> StatusScanResult:
        p = Path(image_path)
        if not p.exists():
            return StatusScanResult(warnings=[f'이미지를 찾지 못했습니다: {p}'])
        return StatusScanResult(warnings=['OCR 미구현: 스테이터스 화면 결과는 사용자가 확인/수정해야 합니다.'])

    def save_pending(self, result: StatusScanResult, path: str | Path = PENDING_SCAN_FILE) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
