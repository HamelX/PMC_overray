from app.data.data_loader import ChampionsData
from app.data.tactical_analyzer import analyze_state
from app.state.current_state import BattleState
from app.state.party_memory import load_party_memory
from app.tactical.move_classifier import classify_move
from app.tactical.tooltip_composer import compose_tooltips


def test_move_classifier_adds_required_tags_from_data():
    data = ChampionsData().load()
    close_combat = next(m for m in data.moves.values() if m.name_ko == '인파이트')
    acrobatics = next(m for m in data.moves.values() if m.name_ko == '애크러뱃')
    fake_out = next(m for m in data.moves.values() if m.name_ko == '속이다')
    assert {'high_risk', 'defense_drop'} <= classify_move(close_combat)
    assert 'variable_power' in classify_move(acrobatics)
    assert {'fake_out', 'priority'} <= classify_move(fake_out)


def test_threat_pipeline_is_data_driven_and_limited():
    report = analyze_state(BattleState(), ChampionsData().load(), load_party_memory('state/party_memory.json'))
    assert 1 <= len(report.opponent_threats) <= 5
    assert report.opponent_threats[0].score >= report.opponent_threats[-1].score
    assert all(threat.short for threat in report.opponent_threats)


def test_tooltip_composer_basic_and_expanded_line_limits():
    report = analyze_state(BattleState(), ChampionsData().load(), load_party_memory('state/party_memory.json'))
    basic = compose_tooltips(report, expanded=False)
    expanded = compose_tooltips(report, expanded=True)
    assert len(next(c for c in basic if c.title == report.opponent.name_ko).lines) <= 4
    assert len(next(c for c in expanded if c.title == report.opponent.name_ko).lines) <= 5


def test_acrobatics_tooltip_prioritizes_condition():
    report = analyze_state(BattleState(), ChampionsData().load(), load_party_memory('state/party_memory.json'))
    cards = compose_tooltips(report, expanded=False)
    acrobatics = next(c for c in cards if c.title == '애크러뱃')
    assert '55→110 조건부' in acrobatics.lines
    assert '조건: 도구 없음' in acrobatics.lines
