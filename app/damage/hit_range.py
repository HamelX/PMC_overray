from __future__ import annotations

import math


def label_hit_range(damage_min: int, damage_max: int, defender_hp: int, measured: bool = False) -> str:
    if defender_hp <= 0 or damage_max < 0:
        return '계산 불가'
    prefix = '실측 ' if measured else '추정 '
    if damage_max == 0:
        return '피해 없음'
    if damage_min >= defender_hp:
        return prefix + '확정 1타'
    if damage_max >= defender_hp:
        return prefix + '난수 1타'
    min_hits = math.ceil(defender_hp / max(damage_max, 1))
    max_hits = math.ceil(defender_hp / max(damage_min, 1)) if damage_min else 999
    if min_hits == 2 and max_hits == 2:
        return prefix + '확정 2타'
    if min_hits == 1 and max_hits <= 2:
        return prefix + '1~2타'
    if min_hits <= 2 and max_hits <= 3:
        return prefix + '2~3타'
    if min_hits <= 3 and max_hits <= 4:
        return prefix + '3~4타'
    return prefix + '4타 이상'
