from app.data.loaders import ChampionsData

def test_loader_search_examples():
    data=ChampionsData().load()
    for name in ['포푸니크','한카리아스','어흥염','리자몽']:
        p=data.get_pokemon(name)
        assert p, name
        assert p.moves
