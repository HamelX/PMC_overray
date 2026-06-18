from app.damage.damage_models import CombatantStats
from app.damage.effective_power_resolver import resolve_effective_power
from app.data.data_loader import ChampionsData


def get_move(name):
    data = ChampionsData().load()
    return next(m for m in data.moves.values() if m.name_ko == name)


def test_acrobatics_doubles_without_item():
    attacker = CombatantStats('포푸니크', 50, 155, 155, 182, 80, 45, 100, 189, item=None)
    defender = CombatantStats('한카리아스', 50, 168, 168, 135, 115, 85, 90, 102)
    result = resolve_effective_power(get_move('애크러뱃'), attacker, defender)
    assert result.base_power == 55
    assert result.effective_power == 110
    assert result.confidence == 'known_rule'


def test_knock_off_needs_context_without_item():
    attacker = CombatantStats('공격자', 50, 100, 100, 100, 100, 100, 100, 100)
    defender = CombatantStats('방어자', 50, 100, 100, 100, 100, 100, 100, 100)
    result = resolve_effective_power(get_move('탁쳐서떨구기'), attacker, defender)
    assert result.confidence == 'needs_context'
