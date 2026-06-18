from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class OCRResult:
    text: str = ''
    confidence: float | None = None
    warnings: list[str] = field(default_factory=list)


class OCREngine:
    """ROI crop 단위 OCR 엔진.

    pytesseract가 설치되어 있으면 사용하고, 없으면 빈 결과와 경고를 반환한다.
    숫자 영역은 숫자 whitelist로 별도 처리할 수 있게 분리했다.
    """

    def __init__(self, language: str = 'kor+eng'):
        self.language = language

    def read_text(self, image, *, numeric: bool = False) -> OCRResult:
        try:
            import pytesseract
        except Exception:
            return OCRResult(warnings=['pytesseract 미설치: OCR 결과 없음'])
        prepared = self.preprocess(image, numeric=numeric)
        config = '--psm 7'
        if numeric:
            config += ' -c tessedit_char_whitelist=0123456789/'
        try:
            text = pytesseract.image_to_string(prepared, lang=self.language, config=config).strip()
        except Exception as exc:
            return OCRResult(warnings=[f'OCR 실패: {exc}'])
        return OCRResult(text=text)

    def preprocess(self, image, *, numeric: bool = False):
        from PIL import ImageFilter, ImageOps

        img = image.convert('L')
        scale = 3 if numeric else 2
        img = img.resize((img.width * scale, img.height * scale))
        img = ImageOps.autocontrast(img)
        threshold = 150 if numeric else 135
        img = img.point(lambda p: 255 if p > threshold else 0)
        return img.filter(ImageFilter.SHARPEN)


def parse_number(text: str) -> int | None:
    match = re.search(r'\d+', text.replace(',', ''))
    return int(match.group(0)) if match else None


def parse_hp(text: str) -> tuple[int | None, int | None]:
    nums = [int(x) for x in re.findall(r'\d+', text.replace(',', ''))]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None
