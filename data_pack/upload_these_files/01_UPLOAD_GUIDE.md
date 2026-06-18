# 업로드 가이드 — Pokémon Champions 전략 지식팩 v2.0

ChatGPT 프로젝트에는 `upload_these_files` 폴더 안 파일만 업로드하면 됩니다.

## 업로드 파일 목록

1. `00_PROJECT_INSTRUCTIONS.md`
2. `02_MECHANICS_AND_TEAM_RULES.md`
3. `03_DATA_SCOPE_VALIDATION.md`
4. `10_CHAMPIONS_CORE_DATABASE_FULL.xlsx`
5. `11_POKEMON_PROFILES_FULL_CLEAN.jsonl`
6. `12_REFERENCE_LOCALIZATION_LOOKUP.csv`
7. `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`
8. `14_POKEMON_INDEX_FULL_CLEAN.csv`
9. `15_MOVES_LINKED_FULL_CLEAN.csv`
10. `16_ITEMS_FULL_CLEAN.csv`
11. `17_ABILITIES_FULL_CLEAN.csv`
12. `18_MANUAL_KO_MOVE_FIXES.csv`
13. `OPGG_FULL_EXTRACTION_REPORT.md`

총 13개 파일입니다. 20개 제한 안에 들어갑니다.

## 기존 프로젝트에서 교체할 파일

기존에 아래 파일이 있으면 삭제하거나 새 파일로 교체하세요.

- `13_POKEMON_MOVES_OPGG_VERIFIED_KO.csv`
- `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv`의 이전 버전
- `10_CHAMPIONS_CORE_DATABASE.xlsx`
- `11_POKEMON_PROFILES.jsonl`

## 테스트 질문

```text
업로드된 Pokémon Champions 전체 데이터 기준으로 답해줘.
포푸니크가 사용할 수 있는 물리 기술 중에서 한카리아스를 때릴 때 유효한 기술을 알려줘.
기술폭은 13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv 기준으로만 판단해줘.
```

## 스프라이트까지 사용할 경우

기본 데이터만 쓰려면 기존 파일들을 업로드하면 된다. 화면 인식/오버레이 개발까지 고려하려면 아래 순서로 스프라이트 manifest를 생성한 뒤 추가 업로드한다.

```powershell
cd optional_tools
py -m venv .venv
.\.venv\Scriptsctivate
pip install requests beautifulsoup4 pandas
python download_champions_menu_sprites.py
python build_sprite_manifest_champions_menu.py
```

생성 후 추가 업로드 권장 파일:

```text
19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv
```

PNG 파일 전체는 ChatGPT 프로젝트에 올리지 않아도 된다. 오버레이 프로그램에서 로컬 경로로 사용하면 된다.
