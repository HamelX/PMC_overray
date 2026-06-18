# Pokémon Champions 전략 지식팩 v2.0 Full Final

이 zip은 OP.GG Pokémon Champions RSC 데이터 추출 결과를 ChatGPT 프로젝트 업로드용으로 정리한 최종 지식팩입니다.

- 포켓몬/폼: 315개
- 포켓몬-기술 연결: 19,742행
- 기술폭 등장 기술: 493개
- 실제 도구: 182개
- 특성: 312개

사용 방법: `upload_these_files` 폴더 안의 파일을 ChatGPT 프로젝트에 업로드하고, `00_PROJECT_INSTRUCTIONS.md` 내용을 프로젝트 지침에 붙여 넣으세요.

## v2.1 Sprite Integration

This version adds optional Pokémon Champions menu sprite integration.

- Source category: Bulbagarden Archives `Category:Champions menu sprites`
- Optional shiny source: `Category:Champions Shiny menu sprites`
- Use `optional_tools/download_champions_menu_sprites.py` then `optional_tools/build_sprite_manifest_champions_menu.py`.
- Upload `19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv` after generating it if you want ChatGPT to reference sprite file paths.

The PNG sprite files are not bundled. The tools download them locally from the public archive and generate a manifest.
