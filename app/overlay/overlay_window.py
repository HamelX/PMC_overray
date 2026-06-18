from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from app.config import DATA_DIR, DEFAULT_TARGET_WINDOW_TITLE, PARTY_MEMORY_FILE, STATE_FILE
from app.data.data_loader import ChampionsData, DataLoadError
from app.data.tactical_analyzer import analyze_state
from app.data.tooltip_builder import build_tooltips
from app.state.current_state import load_current_state
from app.state.party_memory import load_party_memory
from .hotkeys import bind_hotkeys
from .layout import rebuild_cards
from .window_tracker import TrackedWindow


class TacticalOverlayWindow(QWidget):
    """게임 화면 위에 작게 표시되는 전술 툴팁 오버레이."""

    def __init__(self, state_path: Path = STATE_FILE, target_window_title: str = DEFAULT_TARGET_WINDOW_TITLE):
        super().__init__()
        self.state_path = state_path
        self.click_through = False
        self.tracker = TrackedWindow(target_window_title)
        self.data = self._load_data()
        self.party_memory = load_party_memory(PARTY_MEMORY_FILE)

        self.setWindowTitle('Pokémon Champions 전술 툴팁 HUD')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumWidth(300)
        self.setMaximumWidth(390)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.status = QLabel('F8 숨김 · F9 클릭통과 · F10 reload · F11 창찾기 · ESC 종료')
        self.status.setStyleSheet('color: #eeeeee; background: rgba(0,0,0,120); padding: 4px; border-radius: 6px;')
        self.layout.addWidget(self.status)

        bind_hotkeys(
            self,
            toggle_visible=self.toggle_overlay_visible,
            toggle_click_through=self.toggle_click_through,
            reload_state=self.reload_state,
            refind_window=self.refind_window,
            quit_demo=QApplication.instance().quit,
        )
        self.refind_window()
        self.reload_state()

    def _load_data(self) -> ChampionsData | None:
        try:
            return ChampionsData(DATA_DIR).load()
        except DataLoadError:
            return None

    def reload_state(self) -> None:
        state = load_current_state(self.state_path)
        self.party_memory = load_party_memory(PARTY_MEMORY_FILE)
        report = analyze_state(state, self.data, self.party_memory)
        cards = build_tooltips(report)
        # status 라벨은 유지하고 카드만 다시 구성한다.
        while self.layout.count() > 1:
            item = self.layout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        temp = QWidget()
        card_layout = QVBoxLayout(temp)
        card_layout.setContentsMargins(0, 0, 0, 0)
        rebuild_cards(temp, card_layout, cards)
        self.layout.addWidget(temp)
        self.adjustSize()

    def refind_window(self) -> None:
        window = self.tracker.refind()
        x, y = self.tracker.overlay_position()
        self.move(x, y)
        self.status.setText(('창 추적 ON: ' + window.title) if window else 'DEMO: 대상 창 없음 · F11 재탐색')

    def toggle_overlay_visible(self) -> None:
        self.setVisible(not self.isVisible())

    def toggle_click_through(self) -> None:
        self.click_through = not self.click_through
        self.setAttribute(Qt.WA_TransparentForMouseEvents, self.click_through)
        self.setWindowFlag(Qt.WindowTransparentForInput, self.click_through)
        self.show()
        self.status.setText(('클릭 통과 ON' if self.click_through else '클릭 통과 OFF') + ' · F10 reload')
