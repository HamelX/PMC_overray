# 표준 포켓몬 타입 상성표. 공격 타입 -> 방어 타입 배율.
TYPES_KO = {
    "normal":"노말","fire":"불꽃","water":"물","electric":"전기","grass":"풀","ice":"얼음",
    "fighting":"격투","poison":"독","ground":"땅","flying":"비행","psychic":"에스퍼","bug":"벌레",
    "rock":"바위","ghost":"고스트","dragon":"드래곤","dark":"악","steel":"강철","fairy":"페어리",
}
SUPER = {
 "normal":[], "fire":["grass","ice","bug","steel"], "water":["fire","ground","rock"],
 "electric":["water","flying"], "grass":["water","ground","rock"], "ice":["grass","ground","flying","dragon"],
 "fighting":["normal","ice","rock","dark","steel"], "poison":["grass","fairy"], "ground":["fire","electric","poison","rock","steel"],
 "flying":["grass","fighting","bug"], "psychic":["fighting","poison"], "bug":["grass","psychic","dark"],
 "rock":["fire","ice","flying","bug"], "ghost":["psychic","ghost"], "dragon":["dragon"], "dark":["psychic","ghost"],
 "steel":["ice","rock","fairy"], "fairy":["fighting","dragon","dark"]}
NOT = {
 "normal":["rock","steel"], "fire":["fire","water","rock","dragon"], "water":["water","grass","dragon"],
 "electric":["electric","grass","dragon"], "grass":["fire","grass","poison","flying","bug","dragon","steel"], "ice":["fire","water","ice","steel"],
 "fighting":["poison","flying","psychic","bug","fairy"], "poison":["poison","ground","rock","ghost"], "ground":["grass","bug"],
 "flying":["electric","rock","steel"], "psychic":["psychic","steel"], "bug":["fire","fighting","poison","flying","ghost","steel","fairy"],
 "rock":["fighting","ground","steel"], "ghost":["dark"], "dragon":["steel"], "dark":["fighting","dark","fairy"],
 "steel":["fire","water","electric","steel"], "fairy":["fire","poison","steel"]}
IMMUNE = {"normal":["ghost"],"electric":["ground"],"fighting":["ghost"],"poison":["steel"],"ground":["flying"],"psychic":["dark"],"ghost":["normal"],"dragon":["fairy"]}

def effectiveness(attack_type: str, defender_types: list[str] | tuple[str, ...]) -> float:
    attack_type = (attack_type or "").lower()
    mult = 1.0
    for d in defender_types:
        d = (d or "").lower()
        if d in IMMUNE.get(attack_type, []): mult *= 0
        elif d in SUPER.get(attack_type, []): mult *= 2
        elif d in NOT.get(attack_type, []): mult *= 0.5
    return mult

def ko_type(type_id: str) -> str:
    return TYPES_KO.get(type_id, type_id)
