# data_pack

Pokémon Champions 전술 툴팁 HUD는 기본적으로 `data_pack/upload_these_files/` 아래의 로컬 데이터만 읽습니다.

필수 우선순위:

1. `13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv` — 포켓몬별 실제 사용 가능 기술 판단의 최우선 근거
2. `14_POKEMON_INDEX_FULL_CLEAN.csv` — 포켓몬 타입/스탯/특성 ID
3. `15_MOVES_LINKED_FULL_CLEAN.csv` — 기술 타입/분류/위력/우선도/효과문
4. `16_ITEMS_FULL_CLEAN.csv` — 도구 정보
5. `17_ABILITIES_FULL_CLEAN.csv` — 특성 정보
6. `11_POKEMON_PROFILES_FULL_CLEAN.jsonl` — 프로필 보조 데이터

데이터가 없을 때도 앱은 demo tooltip overlay를 띄우며, 데이터 기반 전술 판단은 비활성화됩니다.
