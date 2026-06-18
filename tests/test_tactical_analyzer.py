from app.data.data_loader import ChampionsData
from app.data.tactical_analyzer import analyze_state
from app.state.current_state import BattleState
from app.state.party_memory import load_party_memory


def test_sneasler_vs_garchomp_tactical_report_mentions_key_risks():
    state = BattleState(
        player_active='포푸니크',
        opponent_active='한카리아스',
        player_moves=['인파이트', '속이다', '애크러뱃', '방어'],
    )
    report = analyze_state(state, ChampionsData().load(), load_party_memory('state/party_memory.json'))
    threat_labels = {threat.label for threat in report.opponent_threats}
    assert '지진' in threat_labels
    assert any('setup' in risk.tags for risk in report.opponent_risks)
    assert any(risk.move.name_ko == '속이다' and 'fake_out' in risk.tags for risk in report.player_move_risks)
    assert any(risk.move.name_ko == '인파이트' and 'high_risk' in risk.tags for risk in report.player_move_risks)


def test_tactical_report_contains_damage_results():
    report = analyze_state(BattleState(), ChampionsData().load(), load_party_memory('state/party_memory.json'))
    close_combat = next(r for r in report.player_move_risks if r.move.name_ko == '인파이트')
    acrobatics = next(r for r in report.player_move_risks if r.move.name_ko == '애크러뱃')
    assert close_combat.damage.damage_min > 0
    assert acrobatics.damage.power.effective_power == 110
    assert '추정' in close_combat.damage.hit_range_label
