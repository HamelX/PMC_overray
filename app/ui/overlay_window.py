try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
except ImportError:  # 테스트/서버 환경 배려
    Qt = None; QWidget = object

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.transparent_mode = False
        self.setWindowTitle('Pokémon Champions HUD 오버레이')
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel('전술 보조 오버레이 — 정답 단정 없이 위험/근거만 표시'))
        btn=QPushButton('일반/투명 오버레이 토글')
        btn.clicked.connect(self.toggle_overlay_mode)
        layout.addWidget(btn)
        self.resize(420,160)
    def toggle_overlay_mode(self):
        self.transparent_mode = not self.transparent_mode
        flags = Qt.WindowStaysOnTopHint | Qt.Tool if self.transparent_mode else Qt.Window
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, self.transparent_mode)
        self.setWindowOpacity(0.78 if self.transparent_mode else 1.0)
        self.show()
