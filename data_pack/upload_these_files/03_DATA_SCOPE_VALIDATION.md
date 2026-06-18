# 데이터 범위 및 검증 보고서 — v2.0 Final

## 핵심 검증 결과

| 항목 | 결과 |
|---|---:|
| 포켓몬/폼 | 315 |
| 포켓몬-기술 연결 | 19,742 |
| 기술폭 등장 기술 | 493 |
| 원본 Moves 메타데이터 행 | 598 |
| 실제 도구 행 | 182 |
| 원본 Items_Raw 행 | 204 |
| 특성 행 | 312 |
| 원본 Abilities_Raw 행 | 312 |

## 기술폭 검증

`13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`는 OP.GG Next.js/RSC embedded payload의 포켓몬별 `moves` 배열을 기준으로 정리했다.

주요 검증값:

| 기술 | 연결 수 | 판정 |
|---|---:|---|
| 방어 / protect | 314 | OK |
| 지진 / earthquake | 128 | OK |
| 속이다 / fake-out | 33 | OK |
| 애크러뱃 / acrobatics | 55 | OK |
| 변신 / transform | 1 | OK |

## 도구 데이터 정리

`Items_Raw`에는 총 204행이 있었지만, 이 중 실제 도구 `key/name`이 있는 행은 182개였다. OP.GG 사이트의 서비스 링크/앱 링크처럼 도구가 아닌 행은 `16_ITEMS_FULL_CLEAN.csv`에서 제거했다.

## 특성 데이터 정리

`Abilities_Raw` 312행은 모두 `ability_id`, 한글명, 설명을 가진 특성 데이터로 정리했다.

## 주의사항

- `10_CHAMPIONS_CORE_DATABASE_FULL.xlsx`는 원본 통합 워크북이며, 일부 `name_en` 열이 한국어 페이지 기준 값으로 채워져 있을 수 있다. 답변 시에는 CLEAN CSV/JSONL을 우선 사용한다.
- `15_MOVES_LINKED_FULL_CLEAN.csv`에서 `metadata_source=reference_lookup_fill`인 기술은 OP.GG 기술폭에는 등장하지만, 상세 메타데이터가 부족해 참조표로 타입/분류/한글명을 보강한 기술이다.
- 기술 사용 가능 여부는 반드시 `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`로 판단한다.


## 한글 기술명 보강

참조표에 한글명이 누락되어 영어명으로 남아 있던 기술 14개를 수동 보강했다. 보강 내역은 `18_MANUAL_KO_MOVE_FIXES.csv`에 있다.

보강 후 `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`의 기술명은 모두 한글명 또는 보강 한글명으로 정리했다.
