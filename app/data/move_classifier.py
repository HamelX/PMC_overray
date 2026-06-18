from __future__ import annotations

from dataclasses import dataclass

from .models import Move

PROTECT_NAMES = {'방어', '판별', '킹실드', '니들가드', '토치카', '블로킹', '와이드가드', '퍼스트가드'}
FAKE_OUT_NAMES = {'속이다'}
SETUP_KEYWORDS = ['랭크 올린다', '공격을 2랭크', '특수공격을 2랭크', '스피드를 1랭크', '기세를 높인다']
SETUP_NAMES = {'칼춤', '용의춤', '나쁜음모', '명상', '벌크업', '껍질깨기', '용의춤'}
SPEED_CONTROL_NAMES = {'트릭룸', '순풍', '전기자석파', '얼다바람', '암석봉인', '땅고르기', '실뿜기', '겁나는얼굴'}
STATUS_NAMES = {'수면가루', '버섯포자', '도깨비불', '맹독', '독가루', '전기자석파', '도발', '앵콜', '이상한빛', '하품'}
WEATHER_NAMES = {'비바라기', '쾌청', '모래바람', '설경', '싸라기눈'}
TERRAIN_NAMES = {'일렉트릭필드', '그래스필드', '미스트필드', '사이코필드'}
HAZARD_NAMES = {'스텔스록', '압정뿌리기', '독압정', '끈적끈적네트'}
PIVOT_NAMES = {'유턴', '볼트체인지', '퀵턴', '막말내뱉기', '바톤터치'}
RECOVERY_NAMES = {'HP회복', '날개쉬기', '재생', '달의불빛', '아침햇살', '광합성', '기가드레인', '흡수'}
HIGH_RISK_NAMES = {'인파이트', '브레이브버드', '플레어드라이브', '와일드볼트', '엄청난힘', '오버히트', '리프스톰', '파괴광선', '기가임팩트'}
OHKO_EXPLOSIVE_NAMES = {'땅가르기', '가위자르기', '절대영도', '뿔드릴', '대폭발', '자폭'}


@dataclass(frozen=True)
class ClassifiedMove:
    move: Move
    tags: frozenset[str]


def _priority(move: Move) -> int:
    try:
        return int(move.priority or 0)
    except ValueError:
        return 0


def classify_move(move: Move) -> frozenset[str]:
    """기술명/효과문/우선도/분류 기반 rule-based 태그 분류."""

    name = move.name_ko or move.name_en
    text = getattr(move, 'effect_ko', '') + ' ' + getattr(move, 'description_ko', '')
    tags: set[str] = set()

    if name in PROTECT_NAMES:
        tags.add('protect')
    if name in FAKE_OUT_NAMES:
        tags.add('fake_out')
    if _priority(move) >= 1 and move.category != 'status':
        tags.add('priority')
    if name in SETUP_NAMES or any(k in text for k in SETUP_KEYWORDS):
        tags.add('setup')
    if name in SPEED_CONTROL_NAMES or '스피드를' in text or '트릭룸' in name or '순풍' in name:
        tags.add('speed_control')
    if name in STATUS_NAMES or any(k in text for k in ['마비', '화상', '잠듦', '독 상태', '혼란', '도발', '앵콜']):
        tags.add('status')
    if name in WEATHER_NAMES:
        tags.add('weather')
    if name in TERRAIN_NAMES or '필드' in name:
        tags.add('terrain')
    if name in HAZARD_NAMES:
        tags.add('hazard')
    if name in PIVOT_NAMES or '교대' in text:
        tags.add('pivot')
    if name in RECOVERY_NAMES or 'HP를 회복' in text:
        tags.add('recovery')
    if name in HIGH_RISK_NAMES or any(k in text for k in ['방어와 특수방어가 1랭크 떨어진다', '반동', '다음 턴은 움직일 수 없다']):
        tags.add('high_risk')
    if name in OHKO_EXPLOSIVE_NAMES or '일격' in text:
        tags.add('ohko_or_explosive')
    return frozenset(tags)


def classify_moves(moves: list[Move] | tuple[Move, ...]) -> list[ClassifiedMove]:
    return [ClassifiedMove(move=m, tags=classify_move(m)) for m in moves]
