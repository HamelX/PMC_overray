from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from app.data.data_loader import ChampionsData


@dataclass(frozen=True)
class MatchResult:
    raw: str
    value: str
    id: str | None
    score: float
    matched: bool
    warning: str | None = None


class DataPackFuzzyMatcher:
    def __init__(self, data: ChampionsData, threshold: float = 0.62):
        self.data = data
        self.threshold = threshold
        self.pokemon = [(p.name_ko, p.id) for p in data.pokemon.values()] + [(p.name_en, p.id) for p in data.pokemon.values()]
        self.moves = [(m.name_ko, m.id) for m in data.moves.values()] + [(m.name_en, m.id) for m in data.moves.values()]
        self.items = [(r.get('item_name_ko') or r.get('item_name_en_or_raw') or '', item_id) for item_id, r in data.items.items()]
        self.abilities = [(r.get('ability_name_ko') or r.get('ability_name_en_or_raw') or '', ability_id) for ability_id, r in data.abilities.items()]

    def _match(self, raw: str, choices: list[tuple[str, str]]) -> MatchResult:
        raw_clean = (raw or '').strip()
        if not raw_clean:
            return MatchResult(raw, '', None, 0.0, False, 'OCR 텍스트 없음')
        best_value, best_id, best_score = '', None, 0.0
        for value, value_id in choices:
            if not value:
                continue
            if raw_clean == value:
                return MatchResult(raw, value, value_id, 1.0, True)
            score = SequenceMatcher(None, raw_clean.casefold(), value.casefold()).ratio()
            if raw_clean in value or value in raw_clean:
                score = max(score, 0.88)
            if score > best_score:
                best_value, best_id, best_score = value, value_id, score
        matched = best_score >= self.threshold
        return MatchResult(raw, best_value if matched else raw_clean, best_id if matched else None, best_score, matched, None if matched else '데이터팩 fuzzy match 신뢰도 낮음')

    def pokemon_name(self, raw: str) -> MatchResult:
        return self._match(raw, self.pokemon)

    def move_name(self, raw: str) -> MatchResult:
        return self._match(raw, self.moves)

    def item_name(self, raw: str) -> MatchResult:
        return self._match(raw, self.items)

    def ability_name(self, raw: str) -> MatchResult:
        return self._match(raw, self.abilities)
