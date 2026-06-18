from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QDoubleSpinBox

from app.state.overlay_settings import OverlaySettings


class OverlaySettingsDialog(QDialog):
    def __init__(self, settings: OverlaySettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle('오버레이 설정')
        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.35, 1.0)
        self.opacity.setSingleStep(0.05)
        self.opacity.setValue(settings.opacity)
        self.opacity.setDecimals(2)

        self.width = QSpinBox()
        self.width.setRange(260, 520)
        self.width.setSingleStep(10)
        self.width.setValue(settings.width)

        self.compact = QCheckBox('기본 모드: 짧은 카드')
        self.compact.setChecked(settings.compact_mode)
        self.lock = QCheckBox('위치 잠금')
        self.lock.setChecked(settings.lock_position)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow('투명도', self.opacity)
        layout.addRow('카드 폭', self.width)
        layout.addRow(self.compact)
        layout.addRow(self.lock)
        layout.addRow(buttons)

    def settings(self) -> OverlaySettings:
        return OverlaySettings(
            opacity=float(self.opacity.value()),
            compact_mode=self.compact.isChecked(),
            lock_position=self.lock.isChecked(),
            width=int(self.width.value()),
        )
