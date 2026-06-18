from app.damage.hit_range import label_hit_range


def test_hit_range_labels():
    assert label_hit_range(100, 120, 100, measured=True) == '실측 확정 1타'
    assert label_hit_range(51, 60, 100) == '추정 확정 2타'
    assert label_hit_range(34, 49, 100) == '추정 3~4타'
    assert label_hit_range(0, 0, 100) == '피해 없음'
