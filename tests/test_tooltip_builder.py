from app.data.data_loader import ChampionsData
from app.data.tactical_analyzer import analyze_state
from app.data.tooltip_builder import build_tooltips
from app.state.current_state import BattleState


def test_tooltip_builder_outputs_short_cards_not_type_calculator():
    report = analyze_state(BattleState(), ChampionsData().load())
    cards = build_tooltips(report)
    joined = '\n'.join(line for card in cards for line in card.lines)
    assert any(card.title == '전술 메모' for card in cards)
    assert '상대 지진 보유 가능' in joined
    assert '효과 굉장' not in joined
