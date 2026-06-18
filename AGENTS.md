# AGENTS.md

이 프로젝트는 Pokémon Champions 전술 보조 오버레이/HUD 프로젝트다.

## 핵심 목표

1차 목표는 별도 계산기 앱이 아니라, 게임 화면 위에 툴팁처럼 정보를 표시하는 투명 오버레이를 만드는 것이다.

## 금지 사항

* 게임 메모리 접근 금지
* 패킷 분석 금지
* 프로세스 내부 데이터 접근 금지
* 자동 조작 금지
* 키 입력 자동화 금지
* 매크로/봇 기능 금지

## 허용 사항

* 로컬 CSV/JSONL/XLSX 데이터 조회
* 화면 캡처
* OCR
* 이미지/스프라이트 매칭
* 투명 오버레이 표시
* 사용자가 직접 수정하는 current_state.json 기반 표시

## 1차 MVP 우선순위

1. PySide6 투명 오버레이 창
2. 게임 창 위치 추적
3. click-through 토글
4. 툴팁 카드 렌더링
5. current_state.json reload
6. Pokémon Champions 데이터팩 기반 툴팁 내용 생성

## 데이터 우선순위

* 포켓몬별 사용 가능 기술은 `data_pack/upload_these_files/13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`를 최우선 근거로 사용한다.
* 포켓몬 기본 정보는 `14_POKEMON_INDEX_FULL_CLEAN.csv`와 `11_POKEMON_PROFILES_FULL_CLEAN.jsonl`을 사용한다.
* 기술 정보는 `15_MOVES_LINKED_FULL_CLEAN.csv`를 사용한다.
* 도구 정보는 `16_ITEMS_FULL_CLEAN.csv`를 사용한다.
* 특성 정보는 `17_ABILITIES_FULL_CLEAN.csv`를 사용한다.

## UI 원칙

* 게임 화면을 가리지 않게 작고 반투명한 카드로 표시한다.
* 긴 설명보다 짧은 툴팁 문구를 우선한다.
* “정답 행동”을 단정하지 않는다.
* “유효 타점”, “위험 요소”, “속도 주의”, “교체 고려”처럼 판단 보조 정보만 표시한다.

## 후순위

* OCR
* 스프라이트 자동 인식
* ROI 편집기
* 실제 게임 화면 요소 자동 위치 추정
* 고급 대미지 계산
