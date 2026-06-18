from __future__ import annotations

from dataclasses import dataclass

from app.data.models import Move
from app.data.move_classifier import classify_move as legacy_classify_move

VARIABLE_POWER_NAMES = {'애크러뱃','객기','병상첨병','베놈쇼크','탁쳐서떨구기','웨더볼','자이로볼','일렉트릭볼','풀묶기','안다리걸기','헤비봄버','히트스탬프','분화','해수스파우팅','기사회생','바둥바둥','어시스트파워','파워트립','구르기','아이스볼','보복','눈사태','소금물'}
CHARGING_NAMES = {'파괴광선','기가임팩트','솔라빔','공중날기','구멍파기','다이빙','고스트다이브'}
MULTI_HIT_HINTS = {'2~5회', '연속'}


@dataclass(frozen=True)
class MoveTags:
    move: Move
    tags: frozenset[str]


def classify_move(move: Move) -> frozenset[str]:
    """기술 데이터 기반 태그 분류.

    포켓몬별 문구를 쓰지 않고 기술명/타입/분류/위력/우선도/효과문을 조합한다.
    """

    tags = set(legacy_classify_move(move))
    name = move.name_ko or move.name_en
    text = f'{getattr(move, "description_ko", "")} {getattr(move, "effect_ko", "")}'
    try:
        priority = int(move.priority or 0)
    except ValueError:
        priority = 0

    if name == '트릭룸' or '트릭룸' in text:
        tags.add('trick_room')
        tags.add('speed_control')
    if name == '순풍' or '순풍' in text:
        tags.add('tailwind')
        tags.add('speed_control')
    if '화상' in text or name == '도깨비불':
        tags.update({'status', 'burn'})
    if '마비' in text or name == '전기자석파':
        tags.update({'status', 'paralysis', 'speed_control'})
    if any(word in text for word in ['잠듦', '잠들게', '수면']) or name in {'수면가루', '버섯포자', '최면술'}:
        tags.update({'status', 'sleep'})
    if '독' in text or name in {'맹독', '독가루', '독압정'}:
        tags.update({'status', 'poison'})
    if name in VARIABLE_POWER_NAMES:
        tags.add('variable_power')
    if '방어와 특수방어가 1랭크 떨어진다' in text or '방어가 1랭크 떨어진다' in text:
        tags.add('defense_drop')
        tags.add('high_risk')
    if '반동' in text or name in {'브레이브버드', '플레어드라이브', '와일드볼트'}:
        tags.add('recoil')
        tags.add('high_risk')
    if name in CHARGING_NAMES or '다음 턴은 움직일 수 없다' in text or '1턴째에' in text:
        tags.add('charging')
        tags.add('high_risk')
    if any(hint in text for hint in MULTI_HIT_HINTS):
        tags.add('multi_hit')
    if 'all-other' in getattr(move, 'target', '') or '자신의 주위' in text or '상대 전체' in text:
        tags.add('spread_attack')
    if priority >= 1 and move.category != 'status':
        tags.add('priority')
    return frozenset(tags)


def classify_moves(moves: list[Move] | tuple[Move, ...]) -> list[MoveTags]:
    return [MoveTags(move, classify_move(move)) for move in moves]
