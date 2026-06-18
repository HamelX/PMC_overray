from app.state.pending_scan_result import PendingScanResult, PendingSlotScan


def test_pending_scan_merges_ability_and_status_by_slot():
    ability = PendingScanResult([PendingSlotScan(slot=1, pokemon_name='가디안', pokemon_id='gardevoir', ability='트레이스', item='기합의띠', moves=['트릭룸'], scan_modes=['ability'])])
    status = PendingScanResult([PendingSlotScan(slot=1, pokemon_name='가디안', pokemon_id='gardevoir', current_hp=175, max_hp=175, atk=85, def_=85, spa=194, spd=137, spe=90, scan_modes=['status'])])
    merged = ability.merge(status)
    slot = merged.slots[0]
    assert slot.moves == ['트릭룸']
    assert slot.spa == 194
    assert slot.to_party_pokemon().source == 'status_screen_ocr_confirmed'
