from __future__ import annotations

import math

from app.data.type_chart import effectiveness
from .damage_models import CombatantStats, DamageContext, DamageModifier, DamageResult
from .effective_power_resolver import resolve_effective_power
from .hit_range import label_hit_range


def _stage_multiplier(stage: int) -> float:
    stage = max(-6, min(6, stage))
    return (2 + stage) / 2 if stage >= 0 else 2 / (2 - stage)


def _modified_stat(value: int, stage: int) -> int:
    return max(1, math.floor(value * _stage_multiplier(stage)))


def _boost_value(boosts, attr: str) -> int:
    if not boosts:
        return 0
    if attr == 'def':
        return int(getattr(boosts, 'def_', 0))
    return int(getattr(boosts, attr, 0))


def calculate_damage(context: DamageContext) -> DamageResult:
    move = context.move
    power = resolve_effective_power(move, context.attacker, context.defender, context.field)
    assumptions = [
        '공격자 능력치는 party_memory 실측값 사용' if context.attacker.source_label == '실측' else '공격자 능력치는 추정값 사용',
        f'방어자 능력치는 {context.defender.source_label} 사용',
        '랭크 변화 없음' if not context.attacker_boosts and not context.defender_boosts else '입력된 랭크 변화 반영',
        '도구/특성 보정 일부 미적용',
        *power.assumptions,
    ]
    if move.category == 'status' or power.effective_power <= 0:
        return DamageResult(move.name_ko, context.attacker.name, context.defender.name, 0, 0, 0, 0, '피해 없음', False, False, assumptions, power, defender_source_label=context.defender.source_label)

    attack_stat = context.attacker.atk if move.category == 'physical' else context.attacker.spa
    defense_stat = context.defender.def_ if move.category == 'physical' else context.defender.spd
    attack_stage = _boost_value(context.attacker_boosts, 'atk' if move.category == 'physical' else 'spa')
    defense_stage = _boost_value(context.defender_boosts, 'def' if move.category == 'physical' else 'spd')
    attack_stat = _modified_stat(attack_stat, attack_stage)
    defense_stat = _modified_stat(defense_stat, defense_stage)

    modifiers: list[DamageModifier] = []
    move_type = power.type_override or move.type
    if move_type in context.attacker.types:
        modifiers.append(DamageModifier('stab', 1.5, '자속 보정'))
    type_mult = effectiveness(move_type, context.defender.types)
    modifiers.append(DamageModifier('type', type_mult, '타입 상성 내부 계산'))
    if context.attacker.status in {'burn', '화상'} and move.category == 'physical':
        modifiers.append(DamageModifier('burn', 0.5, '화상 물리 공격 감소'))
    weather = getattr(context.field, 'weather', None)
    if weather in {'rain', '비'} and move_type == 'water':
        modifiers.append(DamageModifier('weather', 1.5, '비 물 기술 강화'))
    if weather in {'rain', '비'} and move_type == 'fire':
        modifiers.append(DamageModifier('weather', 0.5, '비 불꽃 기술 약화'))
    if weather in {'sun', '쾌청'} and move_type == 'fire':
        modifiers.append(DamageModifier('weather', 1.5, '쾌청 불꽃 기술 강화'))
    if weather in {'sun', '쾌청'} and move_type == 'water':
        modifiers.append(DamageModifier('weather', 0.5, '쾌청 물 기술 약화'))
    if context.battle_format == 'double' and getattr(move, 'target', '') == 'all-other-pokemon':
        modifiers.append(DamageModifier('spread', 0.75, '더블 전체기 보정'))

    common_modifier = 1.0
    for mod in modifiers:
        common_modifier *= mod.value
    base = (((((2 * context.attacker.level / 5 + 2) * power.effective_power * attack_stat / max(defense_stat, 1)) / 50) + 2))
    damage_min = math.floor(base * common_modifier * 0.85)
    damage_max = math.floor(base * common_modifier)
    hp = max(context.defender.hp, 1)
    measured = context.defender.source_label == '실측'
    hit_label = label_hit_range(damage_min, damage_max, hp, measured=measured)
    return DamageResult(
        move_name=move.name_ko,
        attacker=context.attacker.name,
        defender=context.defender.name,
        damage_min=damage_min,
        damage_max=damage_max,
        damage_percent_min=round(damage_min * 100 / hp, 1),
        damage_percent_max=round(damage_max * 100 / hp, 1),
        hit_range_label=hit_label,
        is_guaranteed_ohko=damage_min >= hp,
        is_guaranteed_2hko=damage_min * 2 >= hp,
        assumptions=assumptions,
        power=power,
        modifiers=tuple(modifiers),
        defender_source_label=context.defender.source_label,
    )
