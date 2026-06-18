from app.data.loaders import ChampionsData
from app.data.move_classifier import classify_move


def move(name):
    data = ChampionsData().load()
    for m in data.moves.values():
        if m.name_ko == name:
            return m
    raise AssertionError(name)


def test_classifies_key_tactical_tags():
    assert 'fake_out' in classify_move(move('속이다'))
    assert 'protect' in classify_move(move('방어'))
    assert 'setup' in classify_move(move('칼춤'))
    assert 'high_risk' in classify_move(move('인파이트'))
