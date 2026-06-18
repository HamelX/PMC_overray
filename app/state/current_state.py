from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FieldState:
    weather: str | None = None
    terrain: str | None = None
    trick_room: bool = False
    tailwind_player: bool = False
    tailwind_opponent: bool = False


@dataclass
class BattleState:
    player_pokemon: str = '포푸니크'
    opponent_pokemon: str = '한카리아스'
    player_moves: list[str] = field(default_factory=lambda: ['인파이트', '속이다', '애크러뱃', '방어'])
    opponent_team: list[str] = field(default_factory=lambda: ['한카리아스', '어흥염', '리자몽', '마릴리', '팬텀', '토게키스'])
    field: FieldState = field(default_factory=FieldState)
    mode: str = 'demo'

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BattleState':
        field_data = data.get('field') or {}
        return cls(
            player_pokemon=data.get('player_pokemon') or '포푸니크',
            opponent_pokemon=data.get('opponent_pokemon') or '한카리아스',
            player_moves=list(data.get('player_moves') or []),
            opponent_team=list(data.get('opponent_team') or []),
            field=FieldState(**{k: field_data.get(k) for k in FieldState.__dataclass_fields__}),
            mode=data.get('mode') or 'demo',
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'player_pokemon': self.player_pokemon,
            'opponent_pokemon': self.opponent_pokemon,
            'player_moves': self.player_moves,
            'opponent_team': self.opponent_team,
            'field': self.field.__dict__,
            'mode': self.mode,
        }


def load_current_state(path: str | Path) -> BattleState:
    p = Path(path)
    if not p.exists():
        return BattleState()
    return BattleState.from_dict(json.loads(p.read_text(encoding='utf-8')))


def save_current_state(path: str | Path, state: BattleState) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
