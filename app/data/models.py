from dataclasses import dataclass, field

@dataclass(frozen=True)
class Move:
    id: str
    name_en: str
    name_ko: str
    type: str
    type_ko: str
    category: str
    category_ko: str
    power: str = ""
    accuracy: str = ""
    priority: str = ""
    description_ko: str = ""

@dataclass(frozen=True)
class Pokemon:
    id: str
    dex_id: str
    name_en: str
    name_ko: str
    types: tuple[str, ...]
    types_ko: tuple[str, ...]
    abilities: tuple[str, ...]
    stats: dict[str, int]
    moves: tuple[Move, ...] = field(default_factory=tuple)
