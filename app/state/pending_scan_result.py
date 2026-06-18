from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .party_memory import PartyMemory, PartyPokemon, load_party_memory, save_party_memory


@dataclass
class PendingSlotScan:
    slot: int
    pokemon_name: str | None = None
    pokemon_id: str | None = None
    level: int | None = 50
    current_hp: int | None = None
    max_hp: int | None = None
    atk: int | None = None
    def_: int | None = None
    spa: int | None = None
    spd: int | None = None
    spe: int | None = None
    ability: str | None = None
    item: str | None = None
    status: str | None = None
    moves: list[str] = field(default_factory=list)
    scan_modes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PendingSlotScan':
        return cls(
            slot=int(data.get('slot') or 0),
            pokemon_name=data.get('pokemon_name'),
            pokemon_id=data.get('pokemon_id'),
            level=data.get('level'),
            current_hp=data.get('current_hp'),
            max_hp=data.get('max_hp'),
            atk=data.get('atk'),
            def_=data.get('def') or data.get('def_'),
            spa=data.get('spa'),
            spd=data.get('spd'),
            spe=data.get('spe'),
            ability=data.get('ability'),
            item=data.get('item'),
            status=data.get('status'),
            moves=list(data.get('moves') or []),
            scan_modes=list(data.get('scan_modes') or []),
            warnings=list(data.get('warnings') or []),
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
            'scan_modes': self.scan_modes,
            'warnings': self.warnings,
        }

    def merge(self, other: 'PendingSlotScan') -> 'PendingSlotScan':
        merged = PendingSlotScan.from_dict(self.to_dict())
        for field_name in ['pokemon_name', 'pokemon_id', 'level', 'current_hp', 'max_hp', 'atk', 'def_', 'spa', 'spd', 'spe', 'ability', 'item', 'status']:
            value = getattr(other, field_name)
            if value not in (None, '', []):
                setattr(merged, field_name, value)
        if other.moves:
            merged.moves = other.moves
        merged.scan_modes = sorted(set(self.scan_modes + other.scan_modes))
        merged.warnings = self.warnings + other.warnings
        return merged

    def to_party_pokemon(self) -> PartyPokemon | None:
        required = [self.pokemon_name, self.pokemon_id, self.max_hp, self.atk, self.def_, self.spa, self.spd, self.spe]
        if any(v in (None, '') for v in required):
            return None
        return PartyPokemon(
            slot=self.slot,
            pokemon_name=self.pokemon_name or '',
            pokemon_id=self.pokemon_id or '',
            level=int(self.level or 50),
            current_hp=int(self.current_hp or self.max_hp or 1),
            max_hp=int(self.max_hp or self.current_hp or 1),
            atk=int(self.atk or 1),
            def_=int(self.def_ or 1),
            spa=int(self.spa or 1),
            spd=int(self.spd or 1),
            spe=int(self.spe or 1),
            ability=self.ability or '',
            item=self.item,
            status=self.status,
            moves=self.moves,
            source='status_screen_ocr_confirmed',
        )


@dataclass
class PendingScanResult:
    slots: list[PendingSlotScan] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PendingScanResult':
        return cls([PendingSlotScan.from_dict(s) for s in data.get('slots', [])], list(data.get('warnings') or []))

    def to_dict(self) -> dict[str, Any]:
        return {'slots': [s.to_dict() for s in self.slots], 'warnings': self.warnings}

    def merge(self, other: 'PendingScanResult') -> 'PendingScanResult':
        by_slot = {s.slot: s for s in self.slots}
        for slot in other.slots:
            by_slot[slot.slot] = by_slot[slot.slot].merge(slot) if slot.slot in by_slot else slot
        return PendingScanResult([by_slot[k] for k in sorted(by_slot)], self.warnings + other.warnings)


def load_pending_scan(path: str | Path) -> PendingScanResult:
    p = Path(path)
    if not p.exists():
        return PendingScanResult()
    return PendingScanResult.from_dict(json.loads(p.read_text(encoding='utf-8')))


def save_pending_scan(path: str | Path, result: PendingScanResult) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')


def confirm_pending_scan(pending_path: str | Path, party_path: str | Path) -> PartyMemory:
    pending = load_pending_scan(pending_path)
    memory = load_party_memory(party_path)
    for slot in pending.slots:
        pokemon = slot.to_party_pokemon()
        if pokemon:
            memory.upsert_confirmed(pokemon)
    save_party_memory(party_path, memory)
    return memory
