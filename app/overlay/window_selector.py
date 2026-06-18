from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

from app.capture.window_finder import WindowInfo, list_windows
from .window_labels import window_label


class WindowSelectorDialog(QDialog):
    """실행 중인 보이는 창 목록에서 LDPlayer/게임 창을 수동 선택하는 다이얼로그."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('캡처 대상 프로세스/창 선택')
        self.resize(760, 420)
        self.selected_window: WindowInfo | None = None
        self.windows: list[WindowInfo] = []

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['PID', '프로세스', '창 제목', '크기', 'HWND'])
        self.table.doubleClicked.connect(self.accept_selected)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        refresh = QPushButton('새로고침')
        refresh.clicked.connect(self.refresh)
        select = QPushButton('선택')
        select.clicked.connect(self.accept_selected)
        cancel = QPushButton('취소')
        cancel.clicked.connect(self.reject)
        buttons.addWidget(refresh)
        buttons.addWidget(select)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self) -> None:
        self.windows = list_windows()
        self.table.setRowCount(len(self.windows))
        for row, window in enumerate(self.windows):
            values = [str(window.pid or ''), window.process_name, window.title, f'{window.width}x{window.height}', str(window.hwnd)]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()

    def accept_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.windows):
            return
        self.selected_window = self.windows[row]
        self.accept()
