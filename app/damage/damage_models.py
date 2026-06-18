from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.data.models import Move, Pokemon
from app.state.party_memory import PartyPokemon


@dataclass(frozen=True)
class CombatantStats:
    name: str
    level: int
    hp: int
    current_hp: int
    atk: int
    def_: int
    spa: int
    spd: int
    spe: int
    types: tuple[str, ...] = ()
    ability: str = ''
    item: str | None = None
    status: str | None = None
    source_label: str = '추정'


@dataclass(frozen=True)
class PowerResolution:
    base_power: int
    effective_power: int
    type_override: str | None
    reason: str
    confidence: str
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class DamageModifier:
    name: str
    value: float
    reason: str


@dataclass(frozen=True)
class DamageContext:
    attacker: CombatantStats
    defender: CombatantStats
    move: Move
    field: Any = None
    attacker_boosts: Any = None
    defender_boosts: Any = None
    battle_format: str = 'single'


@dataclass(frozen=True)
class DamageResult:
    move_name: str
    attacker: str
    defender: str
    damage_min: int
    damage_max: int
    damage_percent_min: float
    damage_percent_max: float
    hit_range_label: str
    is_guaranteed_ohko: bool
    is_guaranteed_2hko: bool
    assumptions: list[str] = field(default_factory=list)
    power: PowerResolution | None = None
    modifiers: tuple[DamageModifier, ...] = ()
    defender_source_label: str = '추정'


def party_to_combatant(party: PartyPokemon, types: tuple[str, ...]) -> CombatantStats:
    return CombatantStats(
        name=party.pokemon_name,
        level=party.level,
        hp=party.max_hp,
        current_hp=party.current_hp,
        atk=party.atk,
        def_=party.def_,
        spa=party.spa,
        spd=party.spd,
        spe=party.spe,
        types=types,
        ability=party.ability,
        item=party.item,
        status=party.status,
        source_label='실측',
    )


def estimate_combatant(pokemon: Pokemon, profile: str = 'default', level: int = 50) -> CombatantStats:
    base = pokemon.stats
    hp = int(base.get('hp', 1)) + 60
    atk = int(base.get('atk', 1)) + 5
    defense = int(base.get('def', 1)) + 5
    spa = int(base.get('spa', 1)) + 5
    spd = int(base.get('spd', 1)) + 5
    spe = int(base.get('spe', 1)) + 5
    if profile == 'bulky':
        hp = int(hp * 1.08)
        defense = int(defense * 1.12)
        spd = int(spd * 1.12)
    elif profile == 'offensive':
        atk = int(atk * 1.1)
        spa = int(spa * 1.1)
        spe = int(spe * 1.1)
    label = {'default': '기본 추정', 'bulky': '내구 보정 추정', 'offensive': '공격/스피드 추정', 'unknown': '불확실 추정'}.get(profile, '추정')
    return CombatantStats(pokemon.name_ko, level, hp, hp, atk, defense, spa, spd, spe, tuple(pokemon.types), source_label=label)
