from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from app.config import PENDING_SCAN_FILE
from app.data.data_loader import ChampionsData
from app.state.pending_scan_result import PendingScanResult, PendingSlotScan, load_pending_scan, save_pending_scan
from .fuzzy_matcher import DataPackFuzzyMatcher
from .ocr_engine import OCREngine, parse_hp, parse_number
from .roi_profile import DEFAULT_PARTY_ROI_PROFILE, PartyROIProfile, ScanMode

TabGuess = Literal['ability', 'status', 'unknown']


@dataclass
class StatusScanResult:
    mode: ScanMode
    tab_guess: TabGuess = 'unknown'
    slots: list[PendingSlotScan] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    confidence: str = 'pending_user_confirmation'

    def to_pending(self) -> PendingScanResult:
        return PendingScanResult(self.slots, self.warnings)

    def to_dict(self) -> dict[str, Any]:
        return {
            'mode': self.mode,
            'tab_guess': self.tab_guess,
            'slots': [s.to_dict() for s in self.slots],
            'warnings': self.warnings,
            'confidence': self.confidence,
        }


class StatusScreenReader:
    """LDPlayer 파티 정보 화면 ROI OCR 리더.

    전체 화면 OCR이 아니라 734x429 기준 비율 ROI를 현재 이미지 크기에 맞춰 crop한다.
    능력 탭과 스테이터스 탭 결과는 슬롯 번호 기준 pending scan으로 병합할 수 있다.
    """

    def __init__(
        self,
        data: ChampionsData | None = None,
        profile: PartyROIProfile = DEFAULT_PARTY_ROI_PROFILE,
        ocr: OCREngine | None = None,
    ):
        self.data = data
        self.profile = profile
        self.ocr = ocr or OCREngine()
        self.matcher = DataPackFuzzyMatcher(data) if data else None

    def detect_tab(self, image) -> TabGuess:
        # MVP: 선택 탭 초록색 배경 평균을 비교한다. 실패하면 unknown이므로 사용자가 mode를 지정할 수 있다.
        try:
            ability = self._green_score(image.crop(self.profile.ability_tab_indicator.to_pixels(image.size)))
            status = self._green_score(image.crop(self.profile.status_tab_indicator.to_pixels(image.size)))
        except Exception:
            return 'unknown'
        if max(ability, status) < 15:
            return 'unknown'
        return 'ability' if ability >= status else 'status'

    def read(self, image_path: str | Path, mode: ScanMode | None = None) -> StatusScanResult:
        try:
            from PIL import Image
        except Exception:
            return StatusScanResult(mode or 'ability', warnings=['Pillow 미설치: 스캔 불가'], confidence='failed')
        p = Path(image_path)
        if not p.exists():
            return StatusScanResult(mode or 'ability', warnings=[f'이미지를 찾지 못했습니다: {p}'], confidence='failed')
        image = Image.open(p)
        tab_guess = self.detect_tab(image)
        scan_mode: ScanMode = mode or ('status' if tab_guess == 'status' else 'ability')
        slots = [self._read_slot(image, slot.slot, scan_mode) for slot in self.profile.slots]
        warnings = [] if tab_guess != 'unknown' else ['탭 감지 실패: 지정된 scan mode로 처리']
        if tab_guess != 'unknown' and tab_guess != scan_mode:
            warnings.append(f'탭 감지({tab_guess})와 수동 scan mode({scan_mode})가 다릅니다')
        return StatusScanResult(scan_mode, tab_guess, slots, warnings)

    def scan_to_pending(self, image_path: str | Path, mode: ScanMode, pending_path: str | Path = PENDING_SCAN_FILE) -> PendingScanResult:
        result = self.read(image_path, mode)
        pending = load_pending_scan(pending_path).merge(result.to_pending())
        save_pending_scan(pending_path, pending)
        return pending

    def _read_slot(self, image, slot: int, mode: ScanMode) -> PendingSlotScan:
        slot_profile = self.profile.slot(slot)
        fields = slot_profile.ability_fields if mode == 'ability' else slot_profile.status_fields
        raw = {name: self._read_field(image, roi, numeric=(mode == 'status' and name != 'pokemon_name')) for name, roi in fields.items()}
        warnings = [w for result in raw.values() for w in result.warnings]
        if mode == 'ability':
            return self._ability_slot(slot, raw, warnings)
        return self._status_slot(slot, raw, warnings)

    def _read_field(self, image, roi, *, numeric: bool):
        crop = image.crop(roi.to_pixels(image.size))
        return self.ocr.read_text(crop, numeric=numeric)

    def _ability_slot(self, slot: int, raw: dict[str, Any], warnings: list[str]) -> PendingSlotScan:
        pokemon = self._match('pokemon', raw['pokemon_name'].text)
        ability = self._match('ability', raw['ability'].text)
        item = self._match('item', raw['item'].text)
        moves = [self._match('move', raw[f'move_{i}'].text) for i in range(1, 5)]
        warnings.extend([m.warning for m in [pokemon, ability, item, *moves] if m.warning])
        return PendingSlotScan(
            slot=slot,
            pokemon_name=pokemon.value or None,
            pokemon_id=pokemon.id,
            level=50,
            ability=ability.value or None,
            item=item.value or None,
            moves=[m.value for m in moves if m.value],
            scan_modes=['ability'],
            warnings=warnings,
        )

    def _status_slot(self, slot: int, raw: dict[str, Any], warnings: list[str]) -> PendingSlotScan:
        pokemon = self._match('pokemon', raw['pokemon_name'].text)
        current_hp, max_hp = parse_hp(raw['hp'].text)
        warnings.extend([pokemon.warning] if pokemon.warning else [])
        return PendingSlotScan(
            slot=slot,
            pokemon_name=pokemon.value or None,
            pokemon_id=pokemon.id,
            level=50,
            current_hp=current_hp,
            max_hp=max_hp,
            atk=parse_number(raw['atk'].text),
            def_=parse_number(raw['def'].text),
            spa=parse_number(raw['spa'].text),
            spd=parse_number(raw['spd'].text),
            spe=parse_number(raw['spe'].text),
            scan_modes=['status'],
            warnings=warnings,
        )

    def _match(self, kind: str, text: str):
        if not self.matcher:
            from .fuzzy_matcher import MatchResult
            return MatchResult(text, text.strip(), None, 0.0, False, '데이터팩 없음: fuzzy 보정 생략')
        if kind == 'pokemon':
            return self.matcher.pokemon_name(text)
        if kind == 'move':
            return self.matcher.move_name(text)
        if kind == 'item':
            return self.matcher.item_name(text)
        if kind == 'ability':
            return self.matcher.ability_name(text)
        raise ValueError(kind)

    @staticmethod
    def _green_score(image) -> float:
        rgb = image.convert('RGB')
        pixels = list(rgb.getdata())
        if not pixels:
            return 0.0
        return sum(max(0, g - max(r, b)) for r, g, b in pixels) / len(pixels)
