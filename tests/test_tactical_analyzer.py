from app.data.data_loader import ChampionsData
from app.data.tactical_analyzer import analyze_state
from app.state.current_state import BattleState


def test_sneasler_vs_garchomp_tactical_report_mentions_key_risks():
    state = BattleState(
        player_pokemon='포푸니크',
        opponent_pokemon='한카리아스',
        player_moves=['인파이트', '속이다', '애크러뱃', '방어'],
    )
    report = analyze_state(state, ChampionsData().load())
    opponent_moves = {risk.move.name_ko for risk in report.opponent_risks}
    assert '지진' in opponent_moves
    assert any('setup' in risk.tags for risk in report.opponent_risks)
    assert any(risk.move.name_ko == '속이다' and 'fake_out' in risk.tags for risk in report.player_move_risks)
    assert any(risk.move.name_ko == '인파이트' and 'high_risk' in risk.tags for risk in report.player_move_risks)
