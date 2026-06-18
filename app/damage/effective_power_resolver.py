from __future__ import annotations

from app.data.models import Move
from .damage_models import CombatantStats, PowerResolution


def _base_power(move: Move) -> int:
    try:
        return int(move.power or 0)
    except ValueError:
        return 0


def resolve_effective_power(move: Move, attacker: CombatantStats, defender: CombatantStats, field=None) -> PowerResolution:
    """상황 기반 실제 적용 위력 계산. 규칙 추가가 쉬운 rule-based resolver."""

    base = _base_power(move)
    name = move.name_ko
    assumptions: list[str] = []
    if base <= 0:
        return PowerResolution(base, 0, None, '변화기 또는 위력 없음', 'known_rule')

    if name == '애크러뱃':
        if not attacker.item:
            return PowerResolution(base, base * 2, None, '사용자가 도구를 들고 있지 않아 애크러뱃 위력 2배', 'known_rule')
        return PowerResolution(base, base, None, '사용자가 도구를 들고 있어 애크러뱃 기본 위력', 'known_rule')
    if name == '객기':
        if attacker.status in {'burn', 'paralysis', 'poison', 'toxic', '화상', '마비', '독', '맹독'}:
            return PowerResolution(base, base * 2, None, '사용자가 상태이상이라 객기 위력 2배', 'known_rule')
        return PowerResolution(base, base, None, '사용자 상태이상 없음', 'known_rule')
    if name == '병상첨병':
        if defender.status:
            return PowerResolution(base, base * 2, None, '대상이 상태이상이라 병상첨병 위력 2배', 'known_rule')
        return PowerResolution(base, base, None, '대상 상태이상 확인 안 됨', 'needs_context')
    if name == '베놈쇼크':
        if defender.status in {'poison', 'toxic', '독', '맹독'}:
            return PowerResolution(base, base * 2, None, '대상이 독/맹독이라 베놈쇼크 위력 2배', 'known_rule')
        return PowerResolution(base, base, None, '대상 독 여부를 몰라 베놈쇼크 추가 위력 미적용', 'needs_context')
    if name == '탁쳐서떨구기':
        if defender.item:
            return PowerResolution(base, int(base * 1.5), None, '대상이 제거 가능한 도구를 들고 있다고 보고 위력 증가', 'needs_context')
        return PowerResolution(base, base, None, '상대 도구 보유 여부를 몰라 탁쳐서떨구기 추가 위력 미적용', 'needs_context')
    if name == '웨더볼':
        weather = getattr(field, 'weather', None)
        if weather:
            type_map = {'rain': 'water', 'sun': 'fire', 'sand': 'rock', 'snow': 'ice', '비': 'water', '쾌청': 'fire', '모래바람': 'rock', '설경': 'ice'}
            return PowerResolution(base, 100, type_map.get(weather), f'날씨 {weather} 기준 웨더볼 위력/타입 변경', 'known_rule')
        return PowerResolution(base, base, None, '날씨 없음: 웨더볼 기본 위력', 'known_rule')
    if name == '자이로볼':
        power = min(150, max(1, int(25 * defender.spe / max(attacker.spe, 1)) + 1))
        return PowerResolution(base, power, None, '공격자/방어자 스피드 비율로 자이로볼 위력 계산', 'known_rule')
    if name == '일렉트릭볼':
        ratio = attacker.spe / max(defender.spe, 1)
        power = 150 if ratio >= 4 else 120 if ratio >= 3 else 80 if ratio >= 2 else 60 if ratio >= 1 else 40
        return PowerResolution(base, power, None, '공격자/방어자 스피드 비율로 일렉트릭볼 위력 계산', 'known_rule')
    if name in {'풀묶기', '안다리걸기', '헤비봄버', '히트스탬프'}:
        assumptions.append('무게 데이터 미연결: 조건부 위력 기본값 사용')
        return PowerResolution(base, base, None, f'{name} 무게 기반 위력은 TODO', 'needs_context', tuple(assumptions))
    if name in {'분화', '해수스파우팅'}:
        power = max(1, int(150 * attacker.current_hp / max(attacker.hp, 1)))
        return PowerResolution(base, power, None, '사용자 현재 HP 비율로 위력 계산', 'known_rule')
    if name in {'기사회생', '바둥바둥'}:
        ratio = attacker.current_hp / max(attacker.hp, 1)
        power = 200 if ratio <= 0.0417 else 150 if ratio <= 0.1042 else 100 if ratio <= 0.2083 else 80 if ratio <= 0.3542 else 40 if ratio <= 0.6875 else 20
        return PowerResolution(base, power, None, '사용자 현재 HP 비율로 위력 계산', 'known_rule')
    if name in {'어시스트파워', '파워트립'}:
        assumptions.append('랭크 상승 총합 연결 준비: 현재는 기본 위력 사용')
        return PowerResolution(base, base, None, f'{name} 랭크 상승 기반 위력은 TODO', 'needs_context', tuple(assumptions))
    if name in {'구르기', '아이스볼', '보복', '눈사태', '소금물'}:
        assumptions.append('턴 조건/피격 조건/대상 HP 조건 미입력: 기본 위력 사용')
        return PowerResolution(base, base, None, f'{name} 조건부 위력은 TODO', 'needs_context', tuple(assumptions))

    return PowerResolution(base, base, None, '기본 위력 사용', 'known_rule')
