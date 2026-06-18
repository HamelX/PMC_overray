from __future__ import annotations

from dataclasses import dataclass

from .tactical_analyzer import TAG_LABELS, TacticalReport

@dataclass(frozen=True)
class TooltipCardData:
    title: str
    lines: list[str]
    accent: str = '#8bd3ff'


def _tag_text(tags: frozenset[str]) -> str:
    labels = [TAG_LABELS[t] for t in sorted(tags) if t in TAG_LABELS]
    return ', '.join(labels)


def _damage_lines(move_risk) -> list[str]:
    damage = move_risk.damage
    if not damage:
        return []
    if 'fake_out' in move_risk.tags:
        return [
            f'우선도: +{move_risk.move.priority or 0}',
            '용도: 첫 턴 템포 끊기',
            '피해량보다 트릭룸/순풍/랭업 방해 가치',
        ]
    if damage.damage_max <= 0:
        return ['피해량보다 전술 용도 중심', f'타수: {damage.hit_range_label}']
    lines = [
        f'결정력: {damage.damage_min}~{damage.damage_max}',
        f'예상: {damage.damage_percent_min:g}~{damage.damage_percent_max:g}%',
        f'타수: {damage.hit_range_label}',
        f'상대 내구: {damage.defender_source_label}',
    ]
    if damage.power and damage.power.effective_power != damage.power.base_power:
        lines.insert(0, f'조건 위력: {damage.power.base_power} → {damage.power.effective_power}')
        lines.append(f'조건: {damage.power.reason}')
    return lines


def build_tooltips(report: TacticalReport) -> list[TooltipCardData]:
    if not report.data_available:
        return [TooltipCardData('DEMO', ['데이터팩 없이 오버레이 실행 중', 'state/current_state.json 수정 후 F10 reload'], '#ffd166')]
    if not report.player or not report.opponent:
        return [TooltipCardData('상태 확인', report.memo or ['포켓몬 이름을 확인하세요'], '#ff6b6b')]

    opponent_lines = [
        f'{"/".join(report.opponent.types_ko)} · Speed {report.opponent_speed or report.opponent.stats.get("spe", 0)} · 내구 {report.opponent_bulk_label}',
    ]
    for risk in report.opponent_risks[:7]:
        tag = _tag_text(risk.tags)
        suffix = f' [{tag}]' if tag else ''
        opponent_lines.append(f'- {risk.move.name_ko}{suffix}')
    if not report.opponent_risks:
        opponent_lines.append('- 주요 전술 태그 기술 확인 안 됨')

    player_lines = [
        f'{"/".join(report.player.types_ko)} · Speed {report.player_speed or report.player.stats.get("spe", 0)}',
        *[f'- {note}' for note in report.speed_notes[:3]],
    ]
    for move in report.player_move_risks[:4]:
        tag = _tag_text(move.tags)
        player_lines.append(f'- {move.move.name_ko}: {tag or move.notes[0]}')

    move_cards = []
    for move in report.player_move_risks[:4]:
        header = f'{move.move.type_ko}/{move.move.category_ko} 위력 {move.move.power or "-"} 우선도 {move.move.priority or 0}'
        lines = [header, *_damage_lines(move), *[f'리스크: {n}' for n in move.notes[:2]]]
        move_cards.append(TooltipCardData(move.move.name_ko, lines[:8], '#caffbf'))

    memo = TooltipCardData('전술 메모', [f'- {m}' for m in report.memo[:5]], '#ffd166')
    return [TooltipCardData(report.opponent.name_ko, opponent_lines, '#ffadad'), TooltipCardData(report.player.name_ko, player_lines, '#a0c4ff'), *move_cards, memo]
