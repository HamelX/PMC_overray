from app.state.current_state import load_current_state


def test_default_current_state_is_live_mode():
    state = load_current_state('state/current_state.json')
    assert state.mode == 'live'
    assert state.player_active
    assert state.opponent_active
