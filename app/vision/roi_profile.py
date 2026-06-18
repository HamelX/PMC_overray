from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ScanMode = Literal['ability', 'status']


@dataclass(frozen=True)
class NormalizedROI:
    x: float
    y: float
    w: float
    h: float

    def to_pixels(self, image_size: tuple[int, int]) -> tuple[int, int, int, int]:
        width, height = image_size
        left = round(self.x * width)
        top = round(self.y * height)
        right = round((self.x + self.w) * width)
        bottom = round((self.y + self.h) * height)
        return (left, top, right, bottom)


@dataclass(frozen=True)
class SlotROIProfile:
    slot: int
    card: NormalizedROI
    ability_fields: dict[str, NormalizedROI]
    status_fields: dict[str, NormalizedROI]


@dataclass(frozen=True)
class PartyROIProfile:
    base_size: tuple[int, int]
    slots: tuple[SlotROIProfile, ...]
    ability_tab_indicator: NormalizedROI
    status_tab_indicator: NormalizedROI

    def slot(self, slot: int) -> SlotROIProfile:
        return next(s for s in self.slots if s.slot == slot)


def _slot(slot: int, x: float, y: float) -> SlotROIProfile:
    # 734x429 기준 2열 x 3행 카드 배치를 비율로 표현한다.
    card = NormalizedROI(x, y, 0.43, 0.245)
    ability_fields = {
        'pokemon_name': NormalizedROI(x + 0.055, y + 0.026, 0.17, 0.045),
        'ability': NormalizedROI(x + 0.20, y + 0.090, 0.18, 0.038),
        'item': NormalizedROI(x + 0.20, y + 0.132, 0.18, 0.038),
        'move_1': NormalizedROI(x + 0.052, y + 0.162, 0.15, 0.032),
        'move_2': NormalizedROI(x + 0.215, y + 0.162, 0.15, 0.032),
        'move_3': NormalizedROI(x + 0.052, y + 0.202, 0.15, 0.032),
        'move_4': NormalizedROI(x + 0.215, y + 0.202, 0.15, 0.032),
    }
    status_fields = {
        'pokemon_name': NormalizedROI(x + 0.055, y + 0.026, 0.17, 0.045),
        'hp': NormalizedROI(x + 0.205, y + 0.066, 0.12, 0.035),
        'atk': NormalizedROI(x + 0.205, y + 0.101, 0.12, 0.032),
        'def': NormalizedROI(x + 0.205, y + 0.134, 0.12, 0.032),
        'spa': NormalizedROI(x + 0.205, y + 0.166, 0.12, 0.032),
        'spd': NormalizedROI(x + 0.205, y + 0.198, 0.12, 0.032),
        'spe': NormalizedROI(x + 0.205, y + 0.226, 0.12, 0.032),
    }
    return SlotROIProfile(slot, card, ability_fields, status_fields)


DEFAULT_PARTY_ROI_PROFILE = PartyROIProfile(
    base_size=(734, 429),
    ability_tab_indicator=NormalizedROI(0.34, 0.02, 0.13, 0.07),
    status_tab_indicator=NormalizedROI(0.49, 0.02, 0.16, 0.07),
    slots=(
        _slot(1, 0.045, 0.150),
        _slot(2, 0.525, 0.150),
        _slot(3, 0.045, 0.405),
        _slot(4, 0.525, 0.405),
        _slot(5, 0.045, 0.660),
        _slot(6, 0.525, 0.660),
    ),
)
