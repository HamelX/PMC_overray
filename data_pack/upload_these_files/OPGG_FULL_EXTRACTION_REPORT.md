# OP.GG Pokémon Champions Full Data Extraction Report

- Pokemon/forms: 315
- Moves metadata: 598
- Pokemon-move links: 19,742
- Items raw objects: 204
- Abilities raw objects: 312

## Recommended project upload files

- 10_CHAMPIONS_CORE_DATABASE_FULL.xlsx
- 11_POKEMON_PROFILES_FULL.jsonl
- 13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv

## Notes

- Pokemon and Pokemon_Moves are parsed from OP.GG Next.js/RSC embedded payload.
- Moves metadata is crawled through move detail pages using current/prev/next move objects.
- Items/Abilities are best-effort list-page raw object extraction; inspect counts before final use.