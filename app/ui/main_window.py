from pathlib import Path
from PySide6.QtWidgets import *
from .overlay_window import OverlayWindow
from app.data.loaders import ChampionsData, DataLoadError
from app.data.matchup import advisory

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Pokémon Champions 전술 HUD MVP'); self.resize(1100,760)
        self.data=ChampionsData(Path.cwd()/'data_pack'/'upload_these_files')
        try: self.data.load(); error=None
        except DataLoadError as e: error=str(e)
        root=QWidget(); self.setCentralWidget(root); lay=QVBoxLayout(root)
        if error: lay.addWidget(QLabel('데이터 로드 오류:\n'+error)); return
        top=QHBoxLayout(); lay.addLayout(top)
        self.my=QComboBox(); self.foe=QComboBox(); self.my.setEditable(True); self.foe.setEditable(True)
        names=[f'{p.name_ko} / {p.name_en}' for p in self.data.pokemon.values()]
        self.my.addItems(names); self.foe.addItems(names)
        top.addWidget(QLabel('내 포켓몬')); top.addWidget(self.my); top.addWidget(QLabel('상대 포켓몬')); top.addWidget(self.foe)
        btn=QPushButton('분석 갱신'); btn.clicked.connect(self.refresh); top.addWidget(btn)
        ob=QPushButton('오버레이 창 열기'); ob.clicked.connect(lambda: self.open_overlay()); top.addWidget(ob)
        self.out=QTextEdit(); self.out.setReadOnly(True); lay.addWidget(self.out)
        self.overlay=None; self.refresh()
    def _selected(self, combo):
        return self.data.get_pokemon(combo.currentText().split('/')[0].strip())
    def open_overlay(self):
        self.overlay=OverlayWindow(); self.overlay.show()
    def refresh(self):
        my=self._selected(self.my); foe=self._selected(self.foe)
        if not my or not foe: return
        adv=advisory(my, foe)
        def block(p):
            moves=', '.join(f'{m.name_ko}({m.type_ko}/{m.category_ko})' for m in p.moves[:40])
            return f'[{p.name_ko}/{p.name_en}] 타입: {"/".join(p.types_ko)}\n스탯: {p.stats}\n특성ID: {", ".join(p.abilities)}\n사용 가능 기술(상위 40개 표시): {moves}'
        lines=[block(my),'',block(foe),'','유효 타점:']
        lines += ['- '+r['label'] for r in adv['effective_hits'][:12]] or ['- 없음']
        lines += ['','위험 요소 / 상대 주요 타입·기술 후보:']
        lines += [f"- {t['type_ko']} ×{t['multiplier']:g}: {', '.join(t['moves'][:8])}" for t in adv['threats']] or ['- 확인된 2배 이상 위협 없음']
        lines += ['', adv['switch_note'], adv['speed_note'], '※ 이 HUD는 행동을 자동 선택하지 않고 근거 정보만 표시합니다.']
        self.out.setPlainText('\n'.join(lines))
