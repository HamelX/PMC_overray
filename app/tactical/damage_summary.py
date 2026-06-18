from __future__ import annotations

from app.damage.damage_models import DamageResult


def percent_range(result: DamageResult | None) -> str:
    if not result or result.damage_max <= 0:
        return '피해 없음'
    return f'{result.damage_percent_min:g}~{result.damage_percent_max:g}%'


def compact_hit_label(result: DamageResult | None) -> str:
    if not result:
        return '계산 불가'
    return result.hit_range_label.replace('추정 ', '').replace('실측 ', '')


def compact_damage_summary(result: DamageResult | None) -> str:
    if not result:
        return '계산 불가'
    if result.damage_max <= 0:
        return result.hit_range_label
    return f'{percent_range(result)} / {compact_hit_label(result)}'


def evidence_line(result: DamageResult | None) -> str:
    if not result:
        return '근거: 계산 불가'
    attacker = '내 능력치 실측' if any('party_memory 실측값' in a for a in result.assumptions) else '공격자 추정'
    defender = f'상대 내구 {result.defender_source_label}'
    return f'근거: {attacker} / {defender}'
