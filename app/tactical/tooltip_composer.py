from __future__ import annotations

from app.data.tooltip_builder import TooltipCardData
from .damage_summary import compact_damage_summary, evidence_line
from .rules import CARD_LIMITS


def compose_tooltips(report, *, expanded: bool = False) -> list[TooltipCardData]:
    if not report.data_available:
        return [TooltipCardData('DEMO', ['데이터팩 없이 오버레이 실행 중', 'state/current_state.json 수정 후 F10 reload'], '#ffd166')]
    if not report.player or not report.opponent:
        return [TooltipCardData('상태 확인', report.memo or ['포켓몬 이름을 확인하세요'], '#ff6b6b')]
    cards = [
        _opponent_card(report, expanded),
        _player_card(report, expanded),
        *[_move_card(move, expanded) for move in report.player_move_risks[:4]],
        _memo_card(report),
    ]
    return cards


def _opponent_card(report, expanded: bool) -> TooltipCardData:
    limit = CARD_LIMITS['opponent_expanded' if expanded else 'opponent_basic']
    lines: list[str] = []
    for threat in report.opponent_threats[: limit - 1]:
        if expanded:
            lines.append(f'{threat.label}: {threat.short} · {threat.reason}')
        else:
            lines.append(f'⚠ {threat.short}')
    speed = f'SPE {report.opponent_speed} / {report.player.name_ko} {report.player_speed}' if expanded else ('SPE: 내 쪽 우위' if report.player_speed >= report.opponent_speed else 'SPE: 상대 우위')
    lines.append(speed)
    if expanded and len(lines) < limit:
        lines.append(f'상대 내구: {report.opponent_bulk_label}')
    return TooltipCardData(report.opponent.name_ko, lines[:limit], '#ffadad')


def _player_card(report, expanded: bool) -> TooltipCardData:
    limit = CARD_LIMITS['player_expanded' if expanded else 'player_basic']
    lines = [f'SPE {report.player_speed} / 상대 {report.opponent_speed}']
    top = report.opponent_threats[: max(1, limit - 1)]
    lines.extend(f'주의: {t.label}' for t in top)
    if expanded and len(lines) < limit:
        lines.append(f'상대 내구: {report.opponent_bulk_label}')
    return TooltipCardData(report.player.name_ko, lines[:limit], '#a0c4ff')


def _move_card(move_risk, expanded: bool) -> TooltipCardData:
    limit = CARD_LIMITS['move_expanded' if expanded else 'move_basic']
    move = move_risk.move
    damage = move_risk.damage
    lines: list[str] = []
    if 'fake_out' in move_risk.tags:
        lines = [f'우선도 +{move.priority or 0}', '템포 끊기', '방어/고스트 주의']
    else:
        if damage and damage.power and damage.power.effective_power != damage.power.base_power:
            lines.append(f'{damage.power.base_power}→{damage.power.effective_power} 조건부')
        lines.append(compact_damage_summary(damage))
        risk = _compact_risk(move_risk)
        if damage and damage.power and damage.power.effective_power != damage.power.base_power:
            risk = _short_condition(damage.power.reason)
        if risk:
            lines.append(risk)
        if expanded and damage:
            lines.append(evidence_line(damage))
            if damage.power and damage.power.reason != '기본 위력 사용':
                lines.append(f'조건: {damage.power.reason}')
    return TooltipCardData(move.name_ko, lines[:limit], '#caffbf')


def _memo_card(report) -> TooltipCardData:
    lines = [f'- {m}' for m in report.memo[:CARD_LIMITS['memo']]]
    return TooltipCardData('위험 패널', lines, '#ffd166')


def _compact_risk(move_risk) -> str:
    if 'defense_drop' in move_risk.tags:
        return '후: 방어↓ 특방↓'
    if 'recoil' in move_risk.tags:
        return '반동 주의'
    if 'charging' in move_risk.tags:
        return '충전/반동 턴 주의'
    if 'high_risk' in move_risk.tags:
        return '후속 반격 주의'
    if move_risk.notes:
        return move_risk.notes[0].replace('사용 후 하락/반동/충전 등 ', '').replace('첫 턴 ', '')[:28]
    return ''


def _short_condition(reason: str) -> str:
    if '도구를 들고 있지 않아' in reason:
        return '조건: 도구 없음'
    if '상태이상' in reason:
        return '조건: 상태이상'
    if '날씨' in reason:
        return reason[:28]
    return '조건: ' + reason[:24]
