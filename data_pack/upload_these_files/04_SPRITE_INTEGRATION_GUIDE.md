# Pokémon Champions 스프라이트 연동 가이드

이 지식팩은 OP.GG 포켓몬/기술/도구/특성 데이터에 더해, Bulbagarden Archives의 Pokémon Champions 메뉴 스프라이트를 자동으로 내려받고 포켓몬 인덱스와 매칭할 수 있도록 구성되어 있다.

## 스프라이트 출처

- 일반 메뉴 스프라이트 카테고리: `Category:Champions menu sprites`
- 샤이니 메뉴 스프라이트 카테고리: `Category:Champions Shiny menu sprites`

카테고리 페이지는 200개씩 나뉘어 표시되므로, 수동 저장이 아니라 `optional_tools/download_champions_menu_sprites.py`로 전체 카테고리를 순회하는 것을 권장한다.

## 생성 목표

실행 후 아래 파일이 생성된다.

```text
sprites/champions_menu/normal/*.png
sprites/champions_menu/shiny/*.png
sprites/champions_menu/champions_menu_sprites_raw.csv
upload_these_files/19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv
```

`19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv`는 포켓몬 데이터와 스프라이트 파일을 이어주는 기준 파일이다.

## 실행 순서

압축을 푼 폴더에서 PowerShell을 열고:

```powershell
cd optional_tools
py -m venv .venv
.\.venv\Scriptsctivate
python -m pip install --upgrade pip
pip install requests beautifulsoup4 pandas
python download_champions_menu_sprites.py
python build_sprite_manifest_champions_menu.py
```

## 주의

- PNG 원본 파일은 지식팩에 직접 포함하지 않았다. 각 사용자가 출처 사이트에서 직접 내려받도록 도구만 포함했다.
- 스프라이트 파일명은 `Menu CP 0006-Mega X.png`처럼 도감번호와 폼 라벨을 포함한다.
- 매칭 스크립트는 `14_POKEMON_INDEX_FULL_CLEAN.csv`의 포켓몬/폼 데이터와 다운로드된 파일명을 비교해 자동 매칭한다.
- 매칭 신뢰도는 `match_confidence` 컬럼으로 확인한다.

## 오버레이/HUD 개발에서의 활용

- `sprite_path_normal`: 일반 스프라이트 템플릿 경로
- `sprite_path_shiny`: 샤이니 스프라이트 템플릿 경로
- `pokemon_id`: 전략 DB의 포켓몬 ID
- `pokemon_display_ko`: 화면 표시/한국어 안내용 이름

이 manifest를 이용하면 게임 화면의 파티 아이콘을 잘라서 스프라이트 템플릿 매칭에 사용할 수 있다.
