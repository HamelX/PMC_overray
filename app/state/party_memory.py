from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PartyPokemon:
    slot: int
    pokemon_name: str
    pokemon_id: str
    level: int
    current_hp: int
    max_hp: int
    atk: int
    def_: int
    spa: int
    spd: int
    spe: int
    ability: str = ''
    item: str | None = None
    status: str | None = None
    moves: list[str] = field(default_factory=list)
    source: str = 'manual_or_status_screen_confirmed'

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PartyPokemon':
        return cls(
            slot=int(data.get('slot') or 0),
            pokemon_name=data.get('pokemon_name') or '',
            pokemon_id=data.get('pokemon_id') or '',
            level=int(data.get('level') or 50),
            current_hp=int(data.get('current_hp') or data.get('max_hp') or 1),
            max_hp=int(data.get('max_hp') or data.get('current_hp') or 1),
            atk=int(data.get('atk') or 1),
            def_=int(data.get('def') or data.get('def_') or 1),
            spa=int(data.get('spa') or 1),
            spd=int(data.get('spd') or 1),
            spe=int(data.get('spe') or 1),
            ability=data.get('ability') or '',
            item=data.get('item'),
            status=data.get('status'),
            moves=list(data.get('moves') or []),
            source=data.get('source') or 'manual_or_status_screen_confirmed',
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'slot': self.slot,
            'pokemon_name': self.pokemon_name,
            'pokemon_id': self.pokemon_id,
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
            'status': self.status,
            'moves': self.moves,
            'source': self.source,
        }


@dataclass
class PartyMemory:
    party: list[PartyPokemon] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PartyMemory':
        return cls([PartyPokemon.from_dict(row) for row in data.get('party', [])])

    def to_dict(self) -> dict[str, Any]:
        return {'party': [p.to_dict() for p in self.party]}

    def find(self, name_or_id: str) -> PartyPokemon | None:
        key = (name_or_id or '').casefold().strip()
        for pokemon in self.party:
            if key in {pokemon.pokemon_name.casefold(), pokemon.pokemon_id.casefold()}:
                return pokemon
        return None

    def upsert_confirmed(self, pokemon: PartyPokemon) -> None:
        self.party = [p for p in self.party if p.slot != pokemon.slot and p.pokemon_id != pokemon.pokemon_id]
        self.party.append(pokemon)
        self.party.sort(key=lambda p: p.slot)


def load_party_memory(path: str | Path) -> PartyMemory:
    p = Path(path)
    if not p.exists():
        return PartyMemory()
    return PartyMemory.from_dict(json.loads(p.read_text(encoding='utf-8')))


def save_party_memory(path: str | Path, memory: PartyMemory) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(memory.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
