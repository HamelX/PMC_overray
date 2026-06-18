from app.data.type_chart import effectiveness

def test_type_chart_examples():
    assert effectiveness('ice', ('dragon','ground')) == 4
    assert effectiveness('electric', ('ground',)) == 0
    assert effectiveness('fire', ('water','dragon')) == 0.25
