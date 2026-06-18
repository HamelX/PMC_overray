from app.data.data_loader import ChampionsData
from app.vision.fuzzy_matcher import DataPackFuzzyMatcher


def test_fuzzy_matcher_matches_datapack_names():
    matcher = DataPackFuzzyMatcher(ChampionsData().load())
    assert matcher.pokemon_name('포푸니크').id == 'sneasler'
    assert matcher.move_name('인파이트').matched
    assert matcher.item_name('기합의띠').matched
