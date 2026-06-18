from __future__ import annotations

from dataclasses import dataclass, field

from app.damage.damage_calculator import calculate_damage
from app.damage.damage_models import CombatantStats, DamageContext, DamageResult
from app.data.models import Move, Pokemon
from app.data.type_chart import effectiveness
from app.state.current_state import BattleState
from .damage_summary import compact_damage_summary
from .move_classifier import classify_move
from .rules import THREAT_SCORE_RULES


@dataclass(frozen=True)
class ThreatItem:
    label: str
    score: int
    reason: str
    short: str
    move: Move
    tags: frozenset[str]
    damage: DamageResult | None = None
    details: list[str] = field(default_factory=list)


def score_opponent_threats(
    *,
    opponent: Pokemon,
    player: Pokemon,
    opponent_attacker: CombatantStats,
    player_defender: CombatantStats,
    state: BattleState,
    player_party: list[Pokemon] | None = None,
    limit: int = 5,
) -> list[ThreatItem]:
    threats: list[ThreatItem] = []
    party_types = [p.types for p in (player_party or [])]
    for move in opponent.moves:
        tags = classify_move(move)
        damage = None
        score = 0
        details: list[str] = []
        reason = '전술 변수'
        if move.category != 'status':
            damage = calculate_damage(DamageContext(
                attacker=opponent_attacker,
                defender=player_defender,
                move=move,
                field=state.field,
                attacker_boosts=state.boosts.opponent,
                defender_boosts=state.boosts.player,
                battle_format=state.field.battle_format,
            ))
            if damage.is_guaranteed_ohko:
                score += THREAT_SCORE_RULES['guaranteed_ohko']; details.append('확정 1타 가능')
            elif damage.damage_max >= player_defender.hp:
                score += THREAT_SCORE_RULES['possible_ohko']; details.append('난수 1타 가능')
            elif damage.is_guaranteed_2hko:
                score += THREAT_SCORE_RULES['guaranteed_2hko']; details.append('확정 2타 가능')
            if effectiveness(move.type, player.types) >= 2:
                score += THREAT_SCORE_RULES['weakness_hit']; details.append('현재 포켓몬 약점 타점')
                reason = '현재 포켓몬에게 고위험 타점'
            if _party_pressure(move, party_types) >= 2:
                score += THREAT_SCORE_RULES['party_pressure']; details.append('내 파티 복수 타점')
        if opponent_attacker.spe > player_defender.spe and move.category != 'status':
            score += THREAT_SCORE_RULES['opponent_faster']; details.append('상대가 더 빠름')
        for tag in ['priority','fake_out','setup','trick_room','tailwind','status','recovery','protect','speed_control','weather','terrain','hazard','pivot','high_risk','spread_attack']:
            if tag in tags:
                score += THREAT_SCORE_RULES.get(tag, 0)
                details.append(_tag_reason(tag))
                reason = _tag_reason(tag)
        if score <= 0:
            continue
        short = _short_text(move, tags, damage)
        threats.append(ThreatItem(move.name_ko, score, reason, short, move, tags, damage, details))
    return sorted(threats, key=lambda t: (-t.score, t.label))[:limit]


def _party_pressure(move: Move, party_types: list[tuple[str, ...]]) -> int:
    return sum(1 for types in party_types if effectiveness(move.type, types) >= 2)


def _tag_reason(tag: str) -> str:
    return {
        'priority': '우선도 변수', 'fake_out': '첫 턴 템포 변수', 'setup': '랭업 허용 시 다음 턴 위험 증가',
        'trick_room': '트릭룸으로 행동 순서 반전 가능', 'tailwind': '순풍으로 스피드 구도 변화',
        'status': '상태이상/방해 변수', 'recovery': '회복기로 타수 계산 변동', 'protect': '방어로 턴 소모 가능',
        'speed_control': '스피드 조작 가능', 'weather': '날씨 전환 변수', 'terrain': '필드 전환 변수',
        'hazard': '설치기 누적 압박', 'pivot': '교대기로 대면 회피 가능', 'high_risk': '고위력/고위험 기술 변수',
        'spread_attack': '전체기/범위 공격 변수',
    }.get(tag, '전술 변수')


def _short_text(move: Move, tags: frozenset[str], damage: DamageResult | None) -> str:
    if damage and damage.damage_max > 0:
        return f'{move.name_ko} {compact_damage_summary(damage)}'
    if 'setup' in tags:
        return f'{move.name_ko} 방치 위험'
    if 'trick_room' in tags or 'tailwind' in tags:
        return f'{move.name_ko} 속도 구도 변화'
    if 'fake_out' in tags:
        return f'{move.name_ko} 템포 끊기'
    return f'{move.name_ko} {_tag_reason(next(iter(tags), ""))}'
