from .models import Pokemon, Move
from .type_chart import effectiveness, ko_type

def offensive_options(attacker: Pokemon, defender: Pokemon):
    rows=[]
    for m in attacker.moves:
        mult=effectiveness(m.type, defender.types)
        if m.category != 'status':
            rows.append({'move':m,'multiplier':mult,'label':f"{m.name_ko}({ko_type(m.type)}) ×{mult:g}"})
    return sorted(rows, key=lambda r: (-r['multiplier'], r['move'].name_ko))

def threat_types(attacker: Pokemon, defender: Pokemon):
    seen={}
    for m in attacker.moves:
        if m.category == 'status': continue
        mult=effectiveness(m.type, defender.types)
        if mult >= 2:
            seen.setdefault(m.type, {'type':m.type,'type_ko':ko_type(m.type),'multiplier':mult,'moves':[]})['moves'].append(m.name_ko)
    return sorted(seen.values(), key=lambda r: (-r['multiplier'], r['type_ko']))

def advisory(my: Pokemon, foe: Pokemon):
    my_opts=offensive_options(my, foe)[:8]
    foe_threats=threat_types(foe, my)
    speed = '속도 주의: 상대가 더 빠릅니다.' if foe.stats.get('spe',0)>my.stats.get('spe',0) else '속도 참고: 내 포켓몬이 같거나 더 빠릅니다.'
    switch = '교체 고려: 상대의 2배 이상 타점이 확인됩니다.' if foe_threats else '교체 고려: 명확한 2배 이상 위협 타입은 적습니다.'
    return {'effective_hits':my_opts,'threats':foe_threats,'speed_note':speed,'switch_note':switch}
