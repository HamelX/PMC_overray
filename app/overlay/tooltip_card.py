from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from app.data.tooltip_builder import TooltipCardData


class TooltipCard(QFrame):
    def __init__(self, data: TooltipCardData):
        super().__init__()
        self.setObjectName('TooltipCard')
        self.setStyleSheet(f'''
            QFrame#TooltipCard {{
                background-color: rgba(18, 22, 30, 205);
                border: 1px solid {data.accent};
                border-radius: 10px;
            }}
            QLabel {{ color: #f7f7f7; font-size: 12px; }}
            QLabel#Title {{ color: {data.accent}; font-weight: 700; font-size: 14px; }}
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)
        title = QLabel(data.title)
        title.setObjectName('Title')
        layout.addWidget(title)
        for line in data.lines[:9]:
            label = QLabel(line)
            label.setWordWrap(True)
            layout.addWidget(label)
