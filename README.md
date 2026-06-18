# Pokémon Champions 전술 툴팁 HUD

이 레포는 Pokémon Champions 게임 화면 위에 작은 반투명 툴팁 카드를 띄우는 전술 보조 오버레이/HUD 프로젝트입니다.

중요: 기본 타입 상성, 무효, 반감, 효과 굉장함 표시는 게임 UI에 이미 있으므로 이 앱의 1차 목표는 단순 타입 상성 계산기가 아닙니다. 1차 MVP는 `state/current_state.json`에 적힌 현재 대면과 `state/party_memory.json`에 저장된 내 파티 실능력치를 읽고, 사용자가 놓치기 쉬운 **기술폭 기반 위험 정보**, **기술별 결정력/타수**, **짧은 전술 메모**를 게임 화면 위에 표시하는 것입니다.

## 안전 원칙

- 게임 메모리 접근 금지
- 패킷 분석 금지
- 프로세스 내부 데이터 접근 금지
- 자동 조작, 키 입력 자동화, 매크로/봇 기능 금지
- “이번 턴 무조건 이걸 눌러라” 같은 자동 의사결정 금지
- 허용 범위: 로컬 데이터 조회, 투명 오버레이 표시, `current_state.json` 기반 수동 상태 입력, 이후 화면 캡처/OCR/스프라이트 매칭 준비

## 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 실행

```bash
python -m app.main
```

실행하면 frameless / always-on-top / transparent background 툴팁 오버레이가 뜹니다. 대상 창 제목은 기본적으로 `Pokémon Champions`를 찾으며, 찾지 못하면 전체 화면 기준 demo 위치에 표시합니다.

## 상태 입력

1차 MVP는 자동 OCR/스프라이트 인식을 하지 않습니다. 현재 대면은 `state/current_state.json`으로 입력합니다.

```json
{
  "player_pokemon": "포푸니크",
  "opponent_pokemon": "한카리아스",
  "player_moves": ["인파이트", "속이다", "애크러뱃", "방어"],
  "opponent_team": ["한카리아스", "어흥염", "리자몽", "마릴리", "팬텀", "토게키스"],
  "field": {
    "weather": null,
    "terrain": null,
    "trick_room": false,
    "tailwind_player": false,
    "tailwind_opponent": false
  },
  "mode": "demo"
}
```

수정 후 `F10`을 누르면 overlay가 상태와 파티 메모리를 다시 읽습니다.


## 내 파티 실능력치 기억

내 파티의 실능력치는 `state/party_memory.json`에 저장합니다. 처음부터 OCR로 확정하지 않고, 수동 입력 또는 JSON 편집으로 등록하는 구조입니다. 이후 스테이터스 화면 OCR 결과는 바로 확정하지 않고 `state/pending_scan_result.json`에 저장한 뒤 사용자가 확인/수정해 반영합니다. 파티 정보 화면은 전체 화면 OCR이 아니라 734x429 기준 비율 ROI를 현재 LDPlayer 창 크기에 맞춰 crop하는 방식입니다.

```json
{
  "party": [
    {
      "slot": 1,
      "pokemon_name": "포푸니크",
      "pokemon_id": "sneasler",
      "level": 50,
      "current_hp": 155,
      "max_hp": 155,
      "atk": 182,
      "def": 80,
      "spa": 45,
      "spd": 100,
      "spe": 189,
      "ability": "곡예",
      "item": null,
      "status": null,
      "moves": ["인파이트", "속이다", "애크러뱃", "방어"],
      "source": "manual_or_status_screen_confirmed"
    }
  ]
}
```



## 데이터 기반 툴팁 생성 파이프라인

오버레이 문구는 포켓몬별로 직접 작성하지 않습니다. 모든 카드는 다음 순서로 자동 생성됩니다.

```text
현재 상태
→ 포켓몬/기술 데이터 조회
→ 기술 태그 분류
→ 피해량/타수 계산
→ 위협 점수 계산
→ 상위 항목 선택
→ 짧은 템플릿 문장 생성
```

`app/tactical/` 모듈은 이 파이프라인을 담당합니다.

- `move_classifier.py`: 기술명/타입/분류/위력/우선도/효과문 기반 태그 분류
- `threat_scorer.py`: 상대 기술폭에서 현재 대면 위협 점수 계산
- `damage_summary.py`: 피해량/퍼센트/타수 요약
- `tooltip_composer.py`: 기본/확장 모드의 짧은 카드 문장 생성
- `rules.py`: 점수와 카드 줄 수 제한 규칙

기본 모드는 상대 카드 최대 4줄, 내 카드 최대 3줄, 기술 카드 최대 3줄, 위험 패널 최대 5줄만 표시합니다. `current_state.json`의 `mode`를 `expanded`로 바꾸면 근거 줄을 조금 더 보여주되 카드 길이 제한을 유지합니다.




## 현재 대면 변경

더 이상 예시 JSON만 보는 흐름이 아닙니다. 오버레이 상단의 `상태` 버튼을 누르면 현재 대면 설정 창이 열리고, 내 포켓몬/상대 포켓몬/상대 내구 프로필/내 기술 4개/표시 모드를 바꿀 수 있습니다. 저장하면 `state/current_state.json`이 갱신되고 툴팁이 즉시 다시 계산됩니다.

- 내 포켓몬 후보는 `state/party_memory.json`의 파티를 우선 사용합니다.
- 상대 포켓몬 후보는 데이터팩의 포켓몬 목록을 사용합니다.
- 기술별 피해량은 party_memory의 실능력치와 선택한 상대 프로필 기준으로 다시 계산됩니다.

## 오버레이 조작/설정

오버레이는 frameless 창이지만 click-through가 꺼져 있고 위치 잠금이 꺼져 있으면 마우스로 드래그해서 이동할 수 있습니다. 상단 바에는 다음 버튼이 있습니다.

- `상태`: 내 포켓몬/상대 포켓몬/기술/상대 프로필을 바꿔 실제 대면 툴팁을 갱신합니다.
- `설정`: 투명도, 카드 폭, 짧은 카드/확장 카드, 위치 잠금을 조정합니다. 설정은 `state/overlay_settings.json`에 저장됩니다.
- `끄기`: 오버레이 앱을 종료합니다.

설정에서 위치 잠금을 켜면 실수로 오버레이를 끌어 움직이지 않도록 막을 수 있습니다.

## 캡처 대상 창/프로세스 선택

화면 인식이 기본 target title로 잘 잡히지 않으면 `F11`을 눌러 현재 보이는 Windows 창 목록에서 LDPlayer/게임 창을 직접 선택합니다. 선택한 창의 제목, 프로세스명, 마지막 HWND는 `state/target_window.json`에 저장되고 이후 F6/F7 파티 스캔은 선택된 프로세스/창을 우선 캡처합니다. 이 기능은 Windows 창 관리자에 노출되는 창 제목/프로세스명/위치만 사용하며 게임 메모리나 프로세스 내부 데이터에는 접근하지 않습니다.

## 파티 화면 OCR 스캔 플로우

파티 정보 화면은 두 탭을 슬롯 번호 기준으로 따로 읽은 뒤 pending 결과에서 병합합니다.

- `F6`: 현재 LDPlayer/대상 창 화면을 **능력 탭**으로 스캔해 이름, 특성, 도구, 기술 4개를 읽고 `state/pending_scan_result.json`에 저장
- `F7`: 현재 화면을 **스테이터스 탭**으로 스캔해 이름, HP, 공격, 방어, 특수공격, 특수방어, 스피드를 읽고 pending에 병합
- `F12`: 사용자가 pending 결과를 확인한 뒤 `state/party_memory.json`에 확정 반영

OCR은 `app/vision/status_screen_reader.py`가 담당하고, ROI는 `app/vision/roi_profile.py`에 734x429 기준 비율 좌표로 저장되어 있습니다. 한글 OCR과 숫자 OCR은 `app/vision/ocr_engine.py`에서 분리 처리하고, 데이터팩 기준 보정은 `app/vision/fuzzy_matcher.py`가 수행합니다. `pytesseract` 또는 로컬 Tesseract OCR 엔진이 없거나 OCR이 실패하면 빈 결과와 경고를 pending에 남기며, party_memory에는 자동 확정하지 않습니다.

보정 기준은 다음과 같습니다.

- 포켓몬명: `14_POKEMON_INDEX_FULL_CLEAN.csv`
- 기술명: `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`
- 도구명: `16_ITEMS_FULL_CLEAN.csv`
- 특성명: `17_ABILITIES_FULL_CLEAN.csv`

## 결정력/타수 계산

`app/damage/` 아래에 피해 계산 구조를 추가했습니다. 계산은 표준 포켓몬식 구조를 따르며, 보정은 `DamageModifier` 리스트로 쌓아 이후 특성/도구/날씨/필드/랭크/더블 보정을 확장하기 쉽게 했습니다. 상대 실능력치를 모르면 `opponent_profile`에 따라 `default`, `bulky`, `offensive`, `unknown` 추정값을 사용하고 툴팁에 `상대 내구: 기본 추정`처럼 표시합니다.

기술 버튼 툴팁에는 다음이 표시됩니다.

- 결정력: 최소~최대 피해량
- 예상: 상대 HP 대비 퍼센트
- 타수: `추정 2~3타`, `실측 확정 2타` 같은 라벨
- 조건 위력: 애크러뱃 등 위력 변동 기술의 실제 적용 위력
- 리스크: 사용 후 하락/반동/우선도/템포 용도

현재 구현된 대표 조건부 위력 규칙은 애크러뱃, 객기, 병상첨병, 베놈쇼크, 탁쳐서떨구기, 웨더볼, 자이로볼, 일렉트릭볼, 분화/해수스파우팅, 기사회생/바둥바둥입니다. 무게 기반/턴 조건 기반 기술은 TODO assumption을 남기도록 했습니다.

## 핫키

- `F6`: 현재 화면을 능력 탭으로 스캔
- `F7`: 현재 화면을 스테이터스 탭으로 스캔
- `F8`: 오버레이 표시/숨김
- `F9`: click-through on/off
- `F10`: `current_state.json` reload
- `F11`: 실행 중인 창/프로세스 목록에서 LDPlayer 또는 게임 창 선택
- `F12`: pending scan result를 party_memory.json에 확정 반영
- `ESC`: demo mode 종료

## 툴팁 카드

표시는 길게 나열하지 않고 작은 카드로 제한합니다.

- 상대 포켓몬 위험 툴팁: 이름/타입/스피드, 실제 배울 수 있는 위협 기술, 방어/속이다/선공기/랭업/상태/날씨/트릭룸/순풍/필드 변수
- 내 포켓몬 요약 툴팁: 이름/타입/스피드, 누가 빠른지, 현재 대면에서 조심할 기술군, 내 기술 중 전술적으로 의미 있는 기술
- 기술 버튼 툴팁: 기술명, 타입/분류/위력/우선도, 조건 위력, 결정력, 예상 피해 퍼센트, 타수, 사용 후 리스크
- 우측 전술 메모 패널: 현재 대면 핵심 리스크 3~5줄

포푸니크 vs 한카리아스 샘플에서는 다음 종류의 메모가 표시됩니다.

- 한카리아스가 지진 보유 가능
- 한카리아스가 칼춤류 랭업 위험 보유 가능하면 표시
- 포푸니크가 속이다를 보유하면 템포 툴팁 표시
- 인파이트는 사용 후 방어/특방 하락 리스크 표시
- 애크러뱃은 도구 없음이면 55 → 110 조건 위력 표시
- 속이다는 피해량보다 우선도/템포 툴팁 우선 표시
- 상대 내구 추정값이면 `상대 내구: 기본 추정` 표시

## 데이터 위치

데이터는 `data_pack/upload_these_files/` 아래 파일을 사용합니다.

- `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv` — 포켓몬별 사용 가능 기술의 최우선 근거
- `14_POKEMON_INDEX_FULL_CLEAN.csv` — 포켓몬 기본 정보/타입/스탯
- `15_MOVES_LINKED_FULL_CLEAN.csv` — 기술 메타데이터
- `16_ITEMS_FULL_CLEAN.csv` — 도구 정보
- `17_ABILITIES_FULL_CLEAN.csv` — 특성 정보
- `11_POKEMON_PROFILES_FULL_CLEAN.jsonl` — 프로필 보조 데이터

포켓몬별 사용 가능 기술은 반드시 `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv` 기준으로 판단하며, 데이터에 없는 포켓몬-기술 관계는 확정하지 않습니다. 데이터팩이 없어도 demo tooltip overlay는 뜨도록 구성되어 있습니다.

## 기술 태그 분류

`app/data/move_classifier.py`는 기술명/효과문/우선도/분류를 기준으로 다음 태그를 rule-based로 분류합니다.

- `protect`, `fake_out`, `priority`, `setup`, `speed_control`, `status`, `weather`, `terrain`, `hazard`, `pivot`, `recovery`, `high_risk`, `ohko_or_explosive`

이 분류는 완벽한 판정이 아니라, 툴팁에서 놓치기 쉬운 위험 신호를 보여주기 위한 1차 규칙입니다.

## 테스트

```bash
pytest
```

## 이후 단계

이번 작업에서는 자동 OCR/스프라이트 인식을 구현하지 않습니다. 이후 단계에서 화면 캡처 프레임, ROI, OCR, 스프라이트 매칭을 `current_state.json` 갱신 입력원으로 붙일 수 있습니다.
