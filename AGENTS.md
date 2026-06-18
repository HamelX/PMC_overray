# AGENTS.md

이 프로젝트는 Pokémon Champions 전술 보조 오버레이/HUD 개발 프로젝트다.

## 핵심 원칙

- 한국어 주석과 한국어 UI 텍스트를 우선한다.
- 게임 메모리, 패킷, 프로세스 내부 데이터에 접근하지 않는다.
- 자동 조작, 매크로, 입력 자동화, 봇 기능을 만들지 않는다.
- 화면 캡처, OCR, 이미지 매칭, 수동 입력 기반의 정보 표시만 허용한다.
- “이번 턴 정답”을 단정하지 않고, 리스크/보상/근거를 표시하는 보조 도구로 만든다.

## 데이터 우선순위

- 포켓몬별 사용 가능 기술은 `data_pack/upload_these_files/13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`를 최우선 근거로 사용한다.
- 포켓몬 기본 정보는 `14_POKEMON_INDEX_FULL_CLEAN.csv`와 `11_POKEMON_PROFILES_FULL_CLEAN.jsonl`을 사용한다.
- 기술 메타데이터는 `15_MOVES_LINKED_FULL_CLEAN.csv`와 `10_CHAMPIONS_CORE_DATABASE_FULL.xlsx`의 Moves 시트를 사용한다.
- 도구 정보는 `16_ITEMS_FULL_CLEAN.csv`를 사용한다.
- 특성 정보는 `17_ABILITIES_FULL_CLEAN.csv`를 사용한다.
- 데이터에 없는 포켓몬-기술 관계는 확정하지 않는다.

## 권장 기술 스택

- Python 3.11+
- PySide6: 투명 오버레이 UI
- pandas/openpyxl: 데이터 로딩
- mss 또는 dxcam: 화면 캡처
- pywin32: Windows 창 핸들 탐색
- opencv-python/numpy/Pillow: 스프라이트 템플릿 매칭
- pytest: 최소 테스트

## 우선순위

1. 데이터 로더
2. 수동 입력형 대면 분석 UI
3. 창 캡처 프리뷰
4. 스프라이트 manifest 기반 포켓몬 아이콘 매칭
5. 투명 오버레이 표시
6. OCR/자동 인식은 후순위