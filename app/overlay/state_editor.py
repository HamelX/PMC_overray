from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit

from app.data.data_loader import ChampionsData
from app.state.current_state import BattleState
from app.state.party_memory import PartyMemory


class BattleStateEditorDialog(QDialog):
    """current_state.json을 직접 편집하지 않고 현재 대면을 바꾸는 간단 설정 창."""

    def __init__(self, state: BattleState, data: ChampionsData | None, party_memory: PartyMemory, parent=None):
        super().__init__(parent)
        self.setWindowTitle('현재 대면 설정')
        self.data = data
        self.party_memory = party_memory

        self.player = QComboBox()
        self.player.setEditable(True)
        player_names = [p.pokemon_name for p in party_memory.party] or ([state.player_active] if state.player_active else [])
        self.player.addItems(player_names)
        self.player.setCurrentText(state.player_active)

        self.opponent = QComboBox()
        self.opponent.setEditable(True)
        if data:
            self.opponent.addItems([p.name_ko for p in data.pokemon.values()])
        self.opponent.setCurrentText(state.opponent_active)

        self.opponent_profile = QComboBox()
        self.opponent_profile.addItems(['default', 'bulky', 'offensive', 'unknown'])
        self.opponent_profile.setCurrentText(state.opponent_profile)

        moves = state.player_moves or []
        self.moves = [QLineEdit(moves[i] if i < len(moves) else '') for i in range(4)]
        self.mode = QComboBox()
        self.mode.addItems(['live', 'expanded'])
        self.mode.setCurrentText('expanded' if state.mode == 'expanded' else 'live')

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow('내 포켓몬', self.player)
        layout.addRow('상대 포켓몬', self.opponent)
        layout.addRow('상대 내구 프로필', self.opponent_profile)
        for idx, move in enumerate(self.moves, start=1):
            layout.addRow(f'내 기술 {idx}', move)
        layout.addRow('표시 모드', self.mode)
        layout.addRow(buttons)

    def to_state(self, base: BattleState) -> BattleState:
        state = BattleState.from_dict(base.to_dict())
        state.player_active = self.player.currentText().strip() or base.player_active
        state.opponent_active = self.opponent.currentText().strip() or base.opponent_active
        state.opponent_profile = self.opponent_profile.currentText().strip() or 'default'
        state.player_moves = [m.text().strip() for m in self.moves if m.text().strip()]
        state.mode = self.mode.currentText().strip() or 'live'
        state.player_party_source = 'party_memory'
        return state
