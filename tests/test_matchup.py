from app.data.loaders import ChampionsData
from app.data.matchup import advisory

def test_matchup_has_advisory():
    d=ChampionsData().load()
    res=advisory(d.get_pokemon('한카리아스'), d.get_pokemon('리자몽'))
    assert 'effective_hits' in res and 'speed_note' in res
