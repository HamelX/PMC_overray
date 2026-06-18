from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.data.tooltip_builder import TooltipCardData
from .tooltip_card import TooltipCard


def rebuild_cards(container: QWidget, layout: QVBoxLayout, cards: list[TooltipCardData]) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
    for card in cards[:7]:
        layout.addWidget(TooltipCard(card))
    layout.addStretch(1)
