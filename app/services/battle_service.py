import random
import json
from typing import Dict, Any, List, Optional

from ..db.init_db import get_db

# Estado de batalha em memória
BATTLES: Dict[int, Dict[str, Any]] = {}
USER_PROGRESS = {'story': 1}


def calculate_enemy_stats(base_character: dict, phase: int) -> dict:
    multiplier = 1 + (phase - 1) * 0.1
    return {
        'id': base_character['id'],
        'name': base_character['name'],
        'rarity': base_character['rarity'],
        'hp': int(base_character['hp'] * multiplier),
        'max_hp': int(base_character['hp'] * multiplier),
        'attack': int(base_character['attack'] * multiplier),
        'defense': int(base_character['defense'] * multiplier),
        'speed': int(base_character['speed'] * multiplier),
        'image_url': base_character['image_url'],
        'type': 'enemy',
        'skills': json.loads(base_character['active_skills']) if base_character['active_skills'] else ["Ataque Básico"],
        'status': {
            'is_alive': True,
            'is_conscious': True,
            'current_hp': int(base_character['hp'] * multiplier),
            'buffs': [],
            'debuffs': []
        },
        'next_enemy_skill': 0,
        'phase': phase
    }


def get_enemies_for_phase(phase: int, battle_type: str = 'story') -> List[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM characters ORDER BY rarity, id')
    base_characters = cursor.fetchall()
    conn.close()

    enemies: List[dict] = []

    if battle_type == 'story':
        if phase <= 10:
            selected_chars = [base_characters[0], base_characters[1]]
        elif phase <= 20:
            selected_chars = [base_characters[0], base_characters[1], base_characters[2]]
        elif phase <= 30:
            selected_chars = [base_characters[0], base_characters[1], base_characters[2], base_characters[3]]
        else:
            selected_chars = base_characters[:6]

        num_enemies = min(2, len(selected_chars))
        selected_enemies = random.sample(selected_chars, num_enemies)
        for i, base_char in enumerate(selected_enemies):
            enemy = calculate_enemy_stats(base_char, phase)
            enemy['id'] = 1000 + phase * 10 + i
            enemies.append(enemy)

    elif battle_type == 'arena':
        if phase <= 5:
            selected_chars = [base_characters[3], base_characters[4]]
        else:
            selected_chars = [base_characters[5], base_characters[6]]
        for i, base_char in enumerate(selected_chars):
            enemy = calculate_enemy_stats(base_char, phase)
            enemy['id'] = 2000 + phase * 10 + i
            enemies.append(enemy)

    return enemies


def update_combatant_status(combatant: dict, damage: int = 0, heal: int = 0, status_effect: Optional[dict] = None) -> None:
    if damage > 0:
        combatant['status']['current_hp'] = max(0, combatant['status']['current_hp'] - damage)
        if combatant['status']['current_hp'] <= 0:
            combatant['status']['is_alive'] = False
            combatant['status']['is_conscious'] = False
    if heal > 0:
        combatant['status']['current_hp'] = min(combatant['max_hp'], combatant['status']['current_hp'] + heal)
        if combatant['status']['current_hp'] > 0 and not combatant['status']['is_alive']:
            combatant['status']['is_alive'] = True
            combatant['status']['is_conscious'] = True
    if status_effect:
        if status_effect['type'] == 'buff':
            combatant['status']['buffs'].append(status_effect)
        elif status_effect['type'] == 'debuff':
            combatant['status']['debuffs'].append(status_effect)


def select_enemy_target(enemy: dict, player_team: List[dict], battle_type: str = 'story') -> Optional[dict]:
    alive_players = [p for p in player_team if p['status']['is_alive']]
    if not alive_players:
        return None
    if battle_type == 'story':
        return min(alive_players, key=lambda p: p['status']['current_hp'])
    return random.choice(alive_players)


def get_next_actor(battle: dict) -> Optional[int]:
    order = battle['action_order']
    current_idx = battle['turn_idx']
    for i in range(len(order)):
        idx = (current_idx + i) % len(order)
        c = order[idx]
        if c['status']['is_alive'] and c['status']['is_conscious'] and not c['has_acted_this_turn']:
            return idx
    return None


def advance_turn(battle: dict) -> None:
    order = battle['action_order']
    current_idx = battle['turn_idx']
    if current_idx < len(order):
        order[current_idx]['has_acted_this_turn'] = True
    alive = [c for c in order if c['status']['is_alive'] and c['status']['is_conscious']]
    all_acted = all(c['has_acted_this_turn'] for c in alive)
    if all_acted and len(alive) > 0:
        battle['current_round'] += 1
        for c in order:
            c['has_acted_this_turn'] = False
    next_idx = get_next_actor(battle)
    if next_idx is not None:
        battle['turn_idx'] = next_idx
    else:
        battle['status'] = 'finished'
