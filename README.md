# Pokémon Champions 전술 보조 오버레이/HUD MVP

게임 메모리·패킷·프로세스 내부 데이터에 접근하지 않고, 로컬 데이터와 수동 입력/화면 캡처 기반으로 위험 요소와 유효 타점을 보여주는 보조 HUD입니다. 자동 조작, 매크로, 키 입력 자동화, “이번 턴 정답” 추천은 포함하지 않습니다.

## 설치
- 포켓몬/폼: 315개
- 포켓몬-기술 연결: 19,742행
- 기술폭 등장 기술: 493개
- 실제 도구: 182개
- 특성: 312개

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 실행

```bash
python -m app.main
```

앱 실행 중에는 외부 웹 요청을 하지 않고 `data_pack/upload_these_files/`의 로컬 CSV/JSONL만 읽습니다. 데이터가 없으면 누락 파일과 데이터 위치를 한국어 오류로 표시합니다.

## 데이터 위치

필수 파일은 다음 위치에 있어야 합니다.

- `data_pack/upload_these_files/13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv` — 포켓몬별 사용 가능 기술의 최우선 근거
- `data_pack/upload_these_files/14_POKEMON_INDEX_FULL_CLEAN.csv` — 포켓몬 기본 정보/타입/스탯
- `data_pack/upload_these_files/15_MOVES_LINKED_FULL_CLEAN.csv` — 기술 메타데이터
- `data_pack/upload_these_files/16_ITEMS_FULL_CLEAN.csv` — 도구 정보
- `data_pack/upload_these_files/17_ABILITIES_FULL_CLEAN.csv` — 특성 정보
- `data_pack/upload_these_files/11_POKEMON_PROFILES_FULL_CLEAN.jsonl` — 프로필 보조 데이터

## MVP 기능

- 한글명/영문명 검색 및 선택: 예) 포푸니크, 한카리아스, 어흥염, 리자몽
- 선택 포켓몬의 타입, 스탯, 특성 ID, 사용 가능 기술 표시
- 내 기술이 상대에게 들어가는 타입 상성 배율 표시
- 상대가 내 포켓몬을 찌를 수 있는 주요 타입/기술 후보 표시
- 일반 창/반투명 항상 위 오버레이 창 토글 구조
- Windows 창 제목/프로세스명 기반 특정 창 캡처, 전체 화면 fallback, ROI 저장 유틸리티
- `mss` 기반 전체 화면 캡처와 ROI 저장 유틸리티
- 스프라이트 manifest와 OpenCV 템플릿 매칭을 위한 준비 모듈

## 테스트

```bash
pytest
```


## 특정 창 캡처 프리뷰

전체 화면은 정확도가 떨어질 수 있으므로 캡처 모듈은 먼저 Windows 창 제목 또는 프로세스명으로 대상 창을 찾고, 해당 창의 클라이언트 영역만 캡처하도록 준비되어 있습니다. 창을 찾지 못할 때만 전체 화면 fallback을 사용합니다. 이 기능은 Windows 창 관리자에서 공개하는 창 제목/위치/PID만 사용하며, 게임 메모리·패킷·프로세스 내부 데이터에는 접근하지 않습니다.

```python
from app.capture.screen_capture import capture_window

# 제목 또는 프로세스명 중 하나만 지정해도 됩니다.
capture_window(title_keyword="Pokémon Champions", output="capture_preview.png")
capture_window(process_name="Champions.exe", output="capture_preview.png")
```

창 후보 목록이 필요하면 다음 함수를 사용할 수 있습니다.

```python
from app.capture.window_finder import list_windows, filter_windows

for window in filter_windows(list_windows(), title_keyword="champions"):
    print(window)
```

## 스프라이트 다운로드/manifest 준비

스프라이트 PNG가 없어도 앱은 깨지지 않습니다. 이후 이미지 매칭을 쓰려면 선택적으로 다음 도구를 실행합니다. 이 단계에서만 외부 웹 요청이 발생할 수 있습니다.

```bash
python data_pack/optional_tools/download_champions_menu_sprites.py
python data_pack/optional_tools/build_sprite_manifest_champions_menu.py
```

나중에 `19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv`가 생성되면 `app/vision/sprite_manifest.py`의 `load_sprite_manifest()`로 읽을 수 있습니다. 실제 자동 인식은 MVP 범위 밖이며, `app/vision/template_matcher.py`는 샘플/테스트용 OpenCV 템플릿 매칭 함수만 제공합니다.

## 안전 원칙

- 게임 메모리, 패킷, 프로세스 내부 데이터 접근 금지
- 자동 조작, 매크로, 입력 자동화, 봇 기능 금지
- 화면 캡처, OCR, 이미지 매칭, 수동 입력 기반 정보 표시만 허용
- 결과는 정답 행동이 아니라 “위험 요소 / 유효 타점 / 교체 고려 / 속도 주의”로 표시
