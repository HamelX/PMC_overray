from app.damage.damage_calculator import calculate_damage
from app.damage.damage_models import DamageContext, estimate_combatant, party_to_combatant
from app.data.data_loader import ChampionsData
from app.state.party_memory import load_party_memory


def test_close_combat_damage_uses_party_memory_stats():
    data = ChampionsData().load()
    player = data.get_pokemon('포푸니크')
    opponent = data.get_pokemon('한카리아스')
    party = load_party_memory('state/party_memory.json')
    attacker = party_to_combatant(party.find('포푸니크'), player.types)
    defender = estimate_combatant(opponent, 'default')
    move = next(m for m in data.moves.values() if m.name_ko == '인파이트')
    result = calculate_damage(DamageContext(attacker, defender, move))
    assert result.damage_min > 0
    assert result.damage_max >= result.damage_min
    assert '추정' in result.hit_range_label
    assert any('party_memory 실측값' in a for a in result.assumptions)
