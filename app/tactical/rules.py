from __future__ import annotations

THREAT_SCORE_RULES = {
    'guaranteed_ohko': 100,
    'possible_ohko': 80,
    'guaranteed_2hko': 60,
    'weakness_hit': 30,
    'opponent_faster': 20,
    'priority': 25,
    'fake_out': 20,
    'setup': 35,
    'trick_room': 35,
    'tailwind': 35,
    'status': 20,
    'party_pressure': 25,
    'recovery': 15,
    'protect': 10,
    'speed_control': 20,
    'weather': 12,
    'terrain': 12,
    'hazard': 10,
    'pivot': 12,
    'high_risk': 8,
    'spread_attack': 10,
}

CARD_LIMITS = {
    'opponent_basic': 4,
    'opponent_expanded': 5,
    'player_basic': 3,
    'player_expanded': 5,
    'move_basic': 3,
    'move_expanded': 5,
    'memo': 5,
}
