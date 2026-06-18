from app.data.data_loader import ChampionsData
from app.data.tactical_analyzer import analyze_state
from app.data.tooltip_builder import build_tooltips
from app.state.current_state import BattleState
from app.state.party_memory import load_party_memory


def test_tooltip_builder_outputs_short_cards_not_type_calculator():
    report = analyze_state(BattleState(), ChampionsData().load(), load_party_memory('state/party_memory.json'))
    cards = build_tooltips(report)
    joined = '\n'.join(line for card in cards for line in card.lines)
    assert any(card.title == '위험 패널' for card in cards)
    assert '지진' in joined
    assert '효과 굉장' not in joined
    assert '%' in joined
    assert any(len(card.lines) <= 4 for card in cards if card.title == '한카리아스')
