from __future__ import annotations

import json
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any


@dataclass
class FieldState:
    weather: str | None = None
    terrain: str | None = None
    trick_room: bool = False
    reflect_player: bool = False
    reflect_opponent: bool = False
    light_screen_player: bool = False
    light_screen_opponent: bool = False
    tailwind_player: bool = False
    tailwind_opponent: bool = False
    battle_format: str = 'single'


@dataclass
class BoostState:
    atk: int = 0
    def_: int = 0
    spa: int = 0
    spd: int = 0
    spe: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> 'BoostState':
        data = data or {}
        return cls(
            atk=int(data.get('atk') or 0),
            def_=int(data.get('def') or data.get('def_') or 0),
            spa=int(data.get('spa') or 0),
            spd=int(data.get('spd') or 0),
            spe=int(data.get('spe') or 0),
        )

    def to_dict(self) -> dict[str, int]:
        return {'atk': self.atk, 'def': self.def_, 'spa': self.spa, 'spd': self.spd, 'spe': self.spe}


@dataclass
class BattleBoosts:
    player: BoostState = dataclass_field(default_factory=BoostState)
    opponent: BoostState = dataclass_field(default_factory=BoostState)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> 'BattleBoosts':
        data = data or {}
        return cls(player=BoostState.from_dict(data.get('player')), opponent=BoostState.from_dict(data.get('opponent')))

    def to_dict(self) -> dict[str, dict[str, int]]:
        return {'player': self.player.to_dict(), 'opponent': self.opponent.to_dict()}


@dataclass
class BattleState:
    player_active: str = '포푸니크'
    opponent_active: str = '한카리아스'
    player_party_source: str = 'party_memory'
    opponent_profile: str = 'default'
    player_moves: list[str] = dataclass_field(default_factory=lambda: ['인파이트', '속이다', '애크러뱃', '방어'])
    opponent_team: list[str] = dataclass_field(default_factory=lambda: ['한카리아스', '어흥염', '리자몽', '마릴리', '팬텀', '토게키스'])
    field: FieldState = dataclass_field(default_factory=FieldState)
    boosts: BattleBoosts = dataclass_field(default_factory=BattleBoosts)
    mode: str = 'demo'

    @property
    def player_pokemon(self) -> str:
        return self.player_active

    @property
    def opponent_pokemon(self) -> str:
        return self.opponent_active

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BattleState':
        field_data = data.get('field') or {}
        field_values = {k: field_data.get(k, getattr(FieldState(), k)) for k in FieldState.__dataclass_fields__}
        return cls(
            player_active=data.get('player_active') or data.get('player_pokemon') or '포푸니크',
            opponent_active=data.get('opponent_active') or data.get('opponent_pokemon') or '한카리아스',
            player_party_source=data.get('player_party_source') or 'party_memory',
            opponent_profile=data.get('opponent_profile') or 'default',
            player_moves=list(data.get('player_moves') or []),
            opponent_team=list(data.get('opponent_team') or []),
            field=FieldState(**field_values),
            boosts=BattleBoosts.from_dict(data.get('boosts')),
            mode=data.get('mode') or 'demo',
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'player_active': self.player_active,
            'opponent_active': self.opponent_active,
            'player_party_source': self.player_party_source,
            'opponent_profile': self.opponent_profile,
            'player_moves': self.player_moves,
            'opponent_team': self.opponent_team,
            'field': self.field.__dict__,
            'boosts': self.boosts.to_dict(),
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
