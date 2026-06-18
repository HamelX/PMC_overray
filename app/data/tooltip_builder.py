from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TooltipCardData:
    title: str
    lines: list[str]
    accent: str = '#8bd3ff'


def build_tooltips(report) -> list[TooltipCardData]:
    from app.tactical.tooltip_composer import compose_tooltips

    return compose_tooltips(report, expanded=getattr(report, 'mode', 'demo') == 'expanded')
