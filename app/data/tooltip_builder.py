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


def build_tooltips(report: TacticalReport) -> list[TooltipCardData]:
    if not report.data_available:
        return [TooltipCardData('DEMO', ['데이터팩 없이 오버레이 실행 중', 'state/current_state.json 수정 후 F10 reload'], '#ffd166')]
    if not report.player or not report.opponent:
        return [TooltipCardData('상태 확인', report.memo or ['포켓몬 이름을 확인하세요'], '#ff6b6b')]

    opponent_lines = [
        f'{"/".join(report.opponent.types_ko)} · Speed {report.opponent.stats.get("spe", 0)}',
    ]
    for risk in report.opponent_risks[:7]:
        tag = _tag_text(risk.tags)
        suffix = f' [{tag}]' if tag else ''
        opponent_lines.append(f'- {risk.move.name_ko}{suffix}')
    if not report.opponent_risks:
        opponent_lines.append('- 주요 전술 태그 기술 확인 안 됨')

    player_lines = [
        f'{"/".join(report.player.types_ko)} · Speed {report.player.stats.get("spe", 0)}',
        *[f'- {note}' for note in report.speed_notes[:2]],
    ]
    for move in report.player_move_risks[:4]:
        tag = _tag_text(move.tags)
        player_lines.append(f'- {move.move.name_ko}: {tag or move.notes[0]}')

    move_cards = []
    for move in report.player_move_risks[:4]:
        header = f'{move.move.type_ko}/{move.move.category_ko} 위력 {move.move.power or "-"} 우선도 {move.move.priority or 0}'
        move_cards.append(TooltipCardData(move.move.name_ko, [header, *[f'- {n}' for n in move.notes[:3]]], '#caffbf'))

    memo = TooltipCardData('전술 메모', [f'- {m}' for m in report.memo[:5]], '#ffd166')
    return [TooltipCardData(report.opponent.name_ko, opponent_lines, '#ffadad'), TooltipCardData(report.player.name_ko, player_lines, '#a0c4ff'), *move_cards, memo]
