from __future__ import annotations

from dataclasses import dataclass, field

from app.state.current_state import BattleState
from app.state.party_memory import PartyMemory
from .data_loader import ChampionsData, Move, Pokemon
from app.tactical.move_classifier import classify_move, classify_moves
from .type_chart import effectiveness
from app.damage.damage_calculator import calculate_damage
from app.damage.damage_models import DamageContext, DamageResult, estimate_combatant, party_to_combatant
from app.tactical.threat_scorer import ThreatItem, score_opponent_threats

TAG_LABELS = {
    'protect': '방어', 'fake_out': '속이다', 'priority': '선공기', 'setup': '랭업',
    'speed_control': '스피드 조작', 'status': '상태/방해', 'weather': '날씨',
    'terrain': '필드', 'hazard': '설치기', 'pivot': '교대기', 'recovery': '회복',
    'high_risk': '고위험', 'ohko_or_explosive': '일격/자폭',
}

@dataclass
class MoveRisk:
    move: Move
    tags: frozenset[str]
    notes: list[str] = field(default_factory=list)
    damage: DamageResult | None = None

@dataclass
class TacticalReport:
    player: Pokemon | None
    opponent: Pokemon | None
    opponent_risks: list[MoveRisk]
    player_move_risks: list[MoveRisk]
    speed_notes: list[str]
    memo: list[str]
    opponent_threats: list[ThreatItem] = field(default_factory=list)
    data_available: bool = True
    player_speed: int = 0
    opponent_speed: int = 0
    opponent_bulk_label: str = '추정'
    mode: str = 'demo'


def _find_move_by_name(data: ChampionsData, name: str) -> Move | None:
    q = name.casefold().strip()
    for move in data.moves.values():
        if q in {move.name_ko.casefold(), move.name_en.casefold(), move.id.casefold()}:
            return move
    return None


def _risk_notes_for_move(move: Move, tags: frozenset[str], target: Pokemon | None = None) -> list[str]:
    notes: list[str] = []
    if 'protect' in tags:
        notes.append('상대 공격/템포를 한 턴 끊을 수 있으나 연속 사용 실패 위험')
    if 'fake_out' in tags:
        notes.append('첫 턴 템포 끊기 가능: 방어/고스트/정신력류 변수 주의')
    if 'priority' in tags:
        notes.append('우선도 변수: 기본 스피드 열세를 일부 보완 가능')
    if 'setup' in tags:
        notes.append('방치 시 랭업으로 다음 턴 압박이 커질 수 있음')
    if 'speed_control' in tags:
        notes.append('트릭룸/순풍/스피드 하락 등 행동 순서 변동 가능')
    if 'status' in tags:
        notes.append('마비/화상/수면/도발/앵콜 등으로 플랜이 흔들릴 수 있음')
    if 'weather' in tags:
        notes.append('날씨 전환으로 화력/스피드/내구 변수가 생길 수 있음')
    if 'terrain' in tags:
        notes.append('필드 전환으로 선공기/상태기/화력 조건이 바뀔 수 있음')
    if 'pivot' in tags:
        notes.append('교대기 가능: 불리 대면을 유지하지 않고 빠질 수 있음')
    if 'recovery' in tags:
        notes.append('회복기로 계산이 어긋날 수 있음')
    if 'high_risk' in tags:
        notes.append('사용 후 하락/반동/충전 등 후속 반격 리스크 확인')
    if 'ohko_or_explosive' in tags:
        notes.append('일격/자폭류 변수: 안정적인 교환 계산이 어려움')
    if target and move.category != 'status' and effectiveness(move.type, target.types) >= 2:
        notes.append(f'{target.name_ko}에게 압박 타점으로 작동 가능')
    return notes


def analyze_state(state: BattleState, data: ChampionsData | None, party_memory: PartyMemory | None = None) -> TacticalReport:
    if not data or not data.pokemon:
        return TacticalReport(None, None, [], [], ['데이터팩 없음: demo tooltip만 표시'], ['state/current_state.json은 읽었지만 데이터 기반 판단은 비활성'], data_available=False)

    player = data.get_pokemon(state.player_pokemon)
    opponent = data.get_pokemon(state.opponent_pokemon)
    if not player or not opponent:
        return TacticalReport(player, opponent, [], [], ['포켓몬 이름을 데이터에서 찾지 못했습니다'], ['current_state.json 이름을 확인하세요'], data_available=True)

    opponent_risks: list[MoveRisk] = []
    important_tags = {'protect','fake_out','priority','setup','speed_control','status','weather','terrain','hazard','pivot','recovery','high_risk','ohko_or_explosive'}
    for cm in classify_moves(opponent.moves):
        target_pressure = cm.move.category != 'status' and effectiveness(cm.move.type, player.types) >= 2
        if cm.tags & important_tags or target_pressure:
            opponent_risks.append(MoveRisk(cm.move, cm.tags, _risk_notes_for_move(cm.move, cm.tags, player)))

    opponent_risks.sort(key=lambda r: (0 if r.tags & important_tags else 1, r.move.name_ko))

    party_pokemon = party_memory.find(player.id) if party_memory else None
    attacker_stats = party_to_combatant(party_pokemon, player.types) if party_pokemon else estimate_combatant(player, 'default')
    defender_stats = estimate_combatant(opponent, state.opponent_profile)

    player_move_risks: list[MoveRisk] = []
    for name in state.player_moves:
        move = _find_move_by_name(data, name)
        if move:
            tags = classify_move(move)
            notes = _risk_notes_for_move(move, tags, opponent)
            if not notes:
                notes.append('단순 배율보다 상대 교체/방어/특성 변수를 확인')
            damage = calculate_damage(DamageContext(
                attacker=attacker_stats,
                defender=defender_stats,
                move=move,
                field=state.field,
                attacker_boosts=state.boosts.player,
                defender_boosts=state.boosts.opponent,
                battle_format=state.field.battle_format,
            ))
            player_move_risks.append(MoveRisk(move, tags, notes, damage))

    ps, os = attacker_stats.spe, defender_stats.spe
    if state.field.trick_room:
        speed_notes = [f'트릭룸 ON: 기본 스피드 {ps} vs {os}, 느린 쪽 우선 가능', f'상대 내구: {defender_stats.source_label}']
    elif ps > os:
        speed_notes = [f'기본 스피드 {player.name_ko} {ps} > {opponent.name_ko} {os}', '스카프/순풍/선공기 변수는 별도 주의', f'상대 내구: {defender_stats.source_label}']
    elif ps < os:
        speed_notes = [f'기본 스피드 {player.name_ko} {ps} < {opponent.name_ko} {os}', '속이다/방어/선공기 등 템포 수단 확인', f'상대 내구: {defender_stats.source_label}']
    else:
        speed_notes = [f'기본 스피드 동률 {ps}: 동속/보정/도구 변수 주의', f'상대 내구: {defender_stats.source_label}']

    opponent_attacker = estimate_combatant(opponent, state.opponent_profile)
    player_defender = attacker_stats
    party_pokemon_models = [data.get_pokemon(p.pokemon_id) for p in party_memory.party] if party_memory else []
    opponent_threats = score_opponent_threats(
        opponent=opponent,
        player=player,
        opponent_attacker=opponent_attacker,
        player_defender=player_defender,
        state=state,
        player_party=[p for p in party_pokemon_models if p],
        limit=5,
    )
    memo = _build_memo(opponent_threats, player_move_risks, speed_notes)
    return TacticalReport(player, opponent, opponent_risks[:16], player_move_risks, speed_notes, memo, opponent_threats, True, attacker_stats.spe, defender_stats.spe, defender_stats.source_label, state.mode)


def _build_memo(opponent_threats: list[ThreatItem], player_moves: list[MoveRisk], speed_notes: list[str]) -> list[str]:
    memo: list[str] = []
    for threat in opponent_threats[:3]:
        memo.append(threat.short)
    if any('fake_out' in r.tags for r in player_moves):
        memo.append('내 속이다로 템포 조절 가능')
    if any('high_risk' in r.tags for r in player_moves):
        memo.append('고위험 기술 사용 후 후속 반격 주의')
    memo.extend(speed_notes[:1])
    return memo[:5]
