from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.config import DATA_DIR, DEFAULT_TARGET_WINDOW_TITLE, OVERLAY_SETTINGS_FILE, PARTY_MEMORY_FILE, PENDING_SCAN_FILE, STATE_FILE, TARGET_WINDOW_FILE
from app.data.data_loader import ChampionsData, DataLoadError
from app.data.tactical_analyzer import analyze_state
from app.data.tooltip_builder import build_tooltips
from app.state.current_state import load_current_state, save_current_state
from app.state.party_memory import load_party_memory
from app.state.pending_scan_result import confirm_pending_scan
from app.state.target_window import TargetWindowConfig, load_target_window, save_target_window
from app.state.overlay_settings import load_overlay_settings, save_overlay_settings
from app.capture.screen_capture import capture_window_or_fullscreen
from app.vision.status_screen_reader import StatusScreenReader
from .hotkeys import bind_hotkeys
from .settings_dialog import OverlaySettingsDialog
from .state_editor import BattleStateEditorDialog
from .window_selector import WindowSelectorDialog
from .layout import rebuild_cards
from .window_tracker import TrackedWindow


class TacticalOverlayWindow(QWidget):
    """게임 화면 위에 작게 표시되는 전술 툴팁 오버레이."""

    def __init__(self, state_path: Path = STATE_FILE, target_window_title: str = DEFAULT_TARGET_WINDOW_TITLE):
        super().__init__()
        self.state_path = state_path
        self.click_through = False
        self.target_config = load_target_window(TARGET_WINDOW_FILE)
        self.overlay_settings = load_overlay_settings(OVERLAY_SETTINGS_FILE)
        self._drag_offset: QPoint | None = None
        if self.target_config.title_keyword == 'Pokémon Champions' and target_window_title != DEFAULT_TARGET_WINDOW_TITLE:
            self.target_config.title_keyword = target_window_title
        self.tracker = TrackedWindow(self.target_config.title_keyword, self.target_config.process_name)
        self.data = self._load_data()
        self.party_memory = load_party_memory(PARTY_MEMORY_FILE)
        self.status_reader = StatusScreenReader(self.data)

        self.setWindowTitle('Pokémon Champions 전술 툴팁 HUD')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumWidth(260)
        self.setMaximumWidth(520)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        top_bar = QHBoxLayout()
        self.status = QLabel('드래그로 이동 · F6/F7 스캔 · F11 창 선택')
        self.status.setStyleSheet('color: #eeeeee; background: rgba(0,0,0,120); padding: 4px; border-radius: 6px;')
        state_button = QPushButton('상태')
        state_button.clicked.connect(self.open_state_editor)
        settings_button = QPushButton('설정')
        settings_button.clicked.connect(self.open_settings)
        close_button = QPushButton('끄기')
        close_button.clicked.connect(QApplication.instance().quit)
        top_bar.addWidget(self.status, 1)
        top_bar.addWidget(state_button)
        top_bar.addWidget(settings_button)
        top_bar.addWidget(close_button)
        self.layout.addLayout(top_bar)

        bind_hotkeys(
            self,
            toggle_visible=self.toggle_overlay_visible,
            toggle_click_through=self.toggle_click_through,
            reload_state=self.reload_state,
            refind_window=self.open_window_selector,
            quit_demo=QApplication.instance().quit,
            scan_ability=lambda: self.scan_party_screen('ability'),
            scan_status=lambda: self.scan_party_screen('status'),
            confirm_pending=self.confirm_pending_scan,
        )
        self.apply_overlay_settings()
        self.refind_window()
        self.reload_state()


    def apply_overlay_settings(self) -> None:
        self.setWindowOpacity(self.overlay_settings.opacity)
        self.setFixedWidth(self.overlay_settings.width)
        self.status.setToolTip('마우스로 드래그해 오버레이를 이동할 수 있습니다. 설정에서 위치 잠금을 켤 수 있습니다.')


    def open_state_editor(self) -> None:
        state = load_current_state(self.state_path)
        self.party_memory = load_party_memory(PARTY_MEMORY_FILE)
        dialog = BattleStateEditorDialog(state, self.data, self.party_memory, self)
        if dialog.exec():
            new_state = dialog.to_state(state)
            save_current_state(self.state_path, new_state)
            self.reload_state()
            self.status.setText('현재 대면을 저장하고 툴팁을 갱신했습니다')

    def open_settings(self) -> None:
        dialog = OverlaySettingsDialog(self.overlay_settings, self)
        if dialog.exec():
            self.overlay_settings = dialog.settings()
            save_overlay_settings(OVERLAY_SETTINGS_FILE, self.overlay_settings)
            self.apply_overlay_settings()
            self.reload_state()
            self.status.setText('설정을 저장했습니다')

    def _load_data(self) -> ChampionsData | None:
        try:
            return ChampionsData(DATA_DIR).load()
        except DataLoadError:
            return None

    def reload_state(self) -> None:
        state = load_current_state(self.state_path)
        if not self.overlay_settings.compact_mode:
            state.mode = 'expanded'
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
        self.status.setText(('창 추적 ON: ' + window.title) if window else 'DEMO: 대상 창 없음 · F11 선택')


    def open_window_selector(self) -> None:
        dialog = WindowSelectorDialog(self)
        if dialog.exec() and dialog.selected_window:
            selected = dialog.selected_window
            self.tracker.set_selected(selected)
            self.target_config = TargetWindowConfig(
                title_keyword=selected.title,
                process_name=selected.process_name,
                last_hwnd=selected.hwnd,
                last_title=selected.title,
            )
            save_target_window(TARGET_WINDOW_FILE, self.target_config)
            self.refind_window()
            self.status.setText(f'캡처 대상 선택: {selected.process_name or "unknown"} · {selected.title}')

    def toggle_overlay_visible(self) -> None:
        self.setVisible(not self.isVisible())

    def toggle_click_through(self) -> None:
        self.click_through = not self.click_through
        self.setAttribute(Qt.WA_TransparentForMouseEvents, self.click_through)
        self.setWindowFlag(Qt.WindowTransparentForInput, self.click_through)
        self.show()
        self.status.setText(('클릭 통과 ON' if self.click_through else '클릭 통과 OFF') + ' · F10 reload')


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.click_through and not self.overlay_settings.lock_position:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and not self.overlay_settings.lock_position:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = None
        super().mouseReleaseEvent(event)

    def scan_party_screen(self, mode: str) -> None:
        tmp = self.state_path.parent / f'_party_scan_{mode}.png'
        try:
            capture_window_or_fullscreen(title_keyword=self.tracker.title_keyword, process_name=self.tracker.process_name, output=tmp)
            pending = self.status_reader.scan_to_pending(tmp, mode, PENDING_SCAN_FILE)
            self.status.setText(f'{mode} 스캔 pending 저장: {len(pending.slots)}슬롯 · F12 확정')
        except Exception as exc:
            self.status.setText(f'{mode} 스캔 실패: {exc}')

    def confirm_pending_scan(self) -> None:
        try:
            self.party_memory = confirm_pending_scan(PENDING_SCAN_FILE, PARTY_MEMORY_FILE)
            self.reload_state()
            self.status.setText('pending scan result를 party_memory.json에 반영했습니다')
        except Exception as exc:
            self.status.setText(f'pending 확정 실패: {exc}')
