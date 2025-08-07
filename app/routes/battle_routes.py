from flask import Blueprint, request, jsonify
from typing import Any, Dict
from ..db.init_db import get_db
from ..services.battle_service import (
    BATTLES, USER_PROGRESS, get_enemies_for_phase, update_combatant_status,
    select_enemy_target, get_next_actor, advance_turn
)

battle_bp = Blueprint('battle', __name__)


@battle_bp.route('/battle/start', methods=['POST'])
def start_battle():
    data = request.json

    # Criar entrada da batalha no DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO battles (battle_type) VALUES (?)', (data['type'],))
    battle_id = cursor.lastrowid
    conn.commit()

    # Carregar equipe principal
    cursor.execute('SELECT * FROM teams WHERE is_main_team = 1 LIMIT 1')
    team = cursor.fetchone()
    player_team = []
    if team:
        for slot in ['character1_id', 'character2_id', 'character3_id', 'character4_id']:
            if team[slot]:
                cursor.execute('''
                    SELECT pc.*, c.name, c.rarity, c.hp as base_hp, c.attack as base_attack, 
                           c.defense as base_defense, c.speed as base_speed, c.image_url, c.active_skills
                    FROM player_characters pc 
                    JOIN characters c ON pc.character_id = c.id 
                    WHERE pc.id = ?
                ''', (team[slot],))
                pc = cursor.fetchone()
                if pc:
                    player_team.append({
                        'id': pc['id'], 'name': pc['name'], 'rarity': pc['rarity'],
                        'hp': pc['base_hp'] + pc['level'] * 10,
                        'max_hp': pc['base_hp'] + pc['level'] * 10,
                        'attack': pc['base_attack'] + pc['level'] * 2,
                        'defense': pc['base_defense'] + pc['level'] * 1,
                        'speed': pc['base_speed'] + pc['level'] * 1,
                        'image_url': pc['image_url'], 'type': 'player',
                        'skills': [],
                        'status': {
                            'is_alive': True, 'is_conscious': True,
                            'current_hp': pc['base_hp'] + pc['level'] * 10,
                            'buffs': [], 'debuffs': []
                        }
                    })
    conn.close()

    # Enemies
    phase = data.get('phase', 1)
    enemies = get_enemies_for_phase(phase, data['type'])

    # Action order
    all_combatants = player_team + enemies
    action_order = sorted(all_combatants, key=lambda c: -c['speed'])
    for idx, c in enumerate(action_order):
        c['order_idx'] = idx
        c['has_acted_this_turn'] = False

    BATTLES[battle_id] = {
        'player_team': player_team,
        'enemies': enemies,
        'action_order': action_order,
        'turn_idx': 0,
        'battle_type': data['type'],
        'status': 'active',
        'winner': None,
        'phase': phase,
        'current_round': 1,
    }

    return jsonify({
        'battle_id': battle_id,
        'enemies': enemies,
        'player_team': player_team,
        'action_order': action_order,
        'turn_idx': 0,
        'message': 'Batalha iniciada'
    })


@battle_bp.route('/battle/<int:battle_id>/state', methods=['GET'])
def get_battle_state(battle_id: int):
    battle = BATTLES.get(battle_id)
    if not battle:
        return jsonify({'error': 'Batalha não encontrada'}), 404
    return jsonify({
        'player_team': battle['player_team'],
        'enemies': battle['enemies'],
        'action_order': battle['action_order'],
        'turn_idx': battle['turn_idx'],
        'status': battle['status'],
        'winner': battle['winner'],
        'phase': battle.get('phase', 1),
        'current_round': battle.get('current_round', 1)
    })


@battle_bp.route('/battle/<int:battle_id>/action', methods=['POST'])
def battle_action(battle_id: int):
    data = request.json or {}
    battle = BATTLES.get(battle_id)
    if not battle or battle['status'] != 'active':
        return jsonify({'error': 'Batalha não encontrada ou já finalizada'}), 400

    order = battle['action_order']
    current = order[battle['turn_idx']]

    if not current['status']['is_alive'] or not current['status']['is_conscious'] or current['has_acted_this_turn']:
        advance_turn(battle)
        return jsonify({'message': f'{current["name"]} não pode agir agora.', 'turn_idx': battle['turn_idx'], 'action_order': order, 'status': battle['status']})

    # Player action
    if current['type'] == 'player':
        action = data.get('action', 'Ataque Básico')
        target_id = data.get('target_id')
        if action in ['Ataque Básico', 'Ataque Especial']:
            target = next((e for e in battle['enemies'] if e['id'] == target_id and e['status']['is_alive']), None)
            if not target:
                return jsonify({'error': 'Alvo inválido'}), 400
            damage = max(0, (int(current['attack'] * 1.5) if action == 'Ataque Especial' else current['attack']) - target['defense'])
            update_combatant_status(target, damage=damage)
            msg = f'{current["name"]} usou {action} em {target["name"]} causando {damage} de dano.'
        elif action == 'Cura':
            target = next((p for p in battle['player_team'] if p['id'] == target_id and p['status']['is_alive']), None)
            if not target:
                return jsonify({'error': 'Alvo inválido'}), 400
            heal = int(current['attack'] * 0.8)
            update_combatant_status(target, heal=heal)
            msg = f'{current["name"]} curou {target["name"]} em {heal} HP.'
        else:
            return jsonify({'error': 'Ação inválida'}), 400
    else:
        # Enemy action
        target = select_enemy_target(current, battle['player_team'], battle['battle_type'])
        if not target:
            battle['status'] = 'finished'
            battle['winner'] = 'enemy'
            return jsonify({'message': 'Derrota! Todos os personagens foram derrotados.', 'winner': 'enemy', 'status': 'finished'})
        skill_idx = current.get('next_enemy_skill', 0)
        available_skills = current['skills']
        action = available_skills[skill_idx % 2] if len(available_skills) >= 2 else available_skills[0]
        damage = max(0, (int(current['attack'] * 1.5) if action == 'Ataque Especial' else current['attack']) - target['defense'])
        update_combatant_status(target, damage=damage)
        current['next_enemy_skill'] = (skill_idx + 1) % len(available_skills)
        msg = f'{current["name"]} usou {action} em {target["name"]} causando {damage} de dano.'

    # Victory/defeat checks
    if not any(e['status']['is_alive'] for e in battle['enemies']):
        battle['status'] = 'finished'
        battle['winner'] = 'player'
        if battle['battle_type'] == 'story':
            phase = battle.get('phase', 1)
            if USER_PROGRESS['story'] <= phase:
                USER_PROGRESS['story'] = phase + 1
        return jsonify({'message': 'Vitória! Todos os inimigos derrotados.', 'winner': 'player', 'status': 'finished', 'action_order': order})
    if not any(p['status']['is_alive'] for p in battle['player_team']):
        battle['status'] = 'finished'
        battle['winner'] = 'enemy'
        return jsonify({'message': 'Derrota! Todos os personagens foram derrotados.', 'winner': 'enemy', 'status': 'finished', 'action_order': order})

    advance_turn(battle)
    return jsonify({'message': msg, 'turn_idx': battle['turn_idx'], 'action_order': order, 'status': battle['status'], 'current_actor': order[battle['turn_idx']], 'current_round': battle.get('current_round', 1)})
