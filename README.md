# Pokémon Champions 전술 툴팁 HUD

이 레포는 Pokémon Champions 게임 화면 위에 작은 반투명 툴팁 카드를 띄우는 전술 보조 오버레이/HUD 프로젝트입니다.

중요: 기본 타입 상성, 무효, 반감, 효과 굉장함 표시는 게임 UI에 이미 있으므로 이 앱의 1차 목표는 단순 타입 상성 계산기가 아닙니다. 1차 MVP는 `state/current_state.json`에 적힌 현재 대면 정보를 읽고, 사용자가 놓치기 쉬운 **기술폭 기반 위험 정보**와 **짧은 전술 메모**를 게임 화면 위에 표시하는 것입니다.

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

수정 후 `F10`을 누르면 overlay가 상태를 다시 읽습니다.

## 핫키

- `F8`: 오버레이 표시/숨김
- `F9`: click-through on/off
- `F10`: `current_state.json` reload
- `F11`: target window 다시 찾기
- `ESC`: demo mode 종료

## 툴팁 카드

표시는 길게 나열하지 않고 작은 카드로 제한합니다.

- 상대 포켓몬 위험 툴팁: 이름/타입/스피드, 실제 배울 수 있는 위협 기술, 방어/속이다/선공기/랭업/상태/날씨/트릭룸/순풍/필드 변수
- 내 포켓몬 요약 툴팁: 이름/타입/스피드, 누가 빠른지, 현재 대면에서 조심할 기술군, 내 기술 중 전술적으로 의미 있는 기술
- 기술 버튼 툴팁: 기술명, 타입/분류/위력/우선도, 사용 후 리스크, 막히는 조건, 방어/무효/특성 변수
- 우측 전술 메모 패널: 현재 대면 핵심 리스크 3~5줄

포푸니크 vs 한카리아스 샘플에서는 다음 종류의 메모가 표시됩니다.

- 한카리아스가 지진 보유 가능
- 한카리아스가 칼춤류 랭업 위험 보유 가능하면 표시
- 포푸니크가 속이다를 보유하면 템포 툴팁 표시
- 인파이트는 사용 후 방어/특방 하락 리스크 표시

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
