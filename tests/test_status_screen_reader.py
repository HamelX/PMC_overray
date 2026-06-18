from pathlib import Path
import pytest
PIL = pytest.importorskip("PIL.Image")
Image = PIL

from app.data.data_loader import ChampionsData
from app.vision.ocr_engine import OCRResult
from app.vision.status_screen_reader import StatusScreenReader


class FakeOCR:
    def __init__(self, values):
        self.values = list(values)
    def read_text(self, image, *, numeric=False):
        return OCRResult(self.values.pop(0) if self.values else '')


def test_status_screen_reader_reads_ability_slots_with_fuzzy_match(tmp_path: Path):
    image_path = tmp_path / 'party.png'
    Image.new('RGB', (734, 429), (20, 20, 20)).save(image_path)
    values = []
    for _ in range(6):
        values += ['포푸니크', '곡예', '기합의띠', '인파이트', '속이다', '애크러뱃', '방어']
    reader = StatusScreenReader(ChampionsData().load(), ocr=FakeOCR(values))
    result = reader.read(image_path, mode='ability')
    assert result.slots[0].pokemon_id == 'sneasler'
    assert result.slots[0].moves[:2] == ['인파이트', '속이다']
