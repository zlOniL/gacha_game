from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import random
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'gacha_game.db'

# Estado temporário das batalhas (em memória)
BATTLES = {}
# Progresso de fases por usuário (simples, para demo)
USER_PROGRESS = {'story': 1}  # Fase máxima liberada

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Criar tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            image_url TEXT,
            active_skills TEXT,
            passive_skills TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            hp_bonus INTEGER DEFAULT 0,
            attack_bonus INTEGER DEFAULT 0,
            defense_bonus INTEGER DEFAULT 0,
            speed_bonus INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            equipment_weapon INTEGER,
            equipment_armor INTEGER,
            equipment_accessory INTEGER,
            FOREIGN KEY (character_id) REFERENCES characters (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            character1_id INTEGER,
            character2_id INTEGER,
            character3_id INTEGER,
            character4_id INTEGER,
            is_main_team BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (character1_id) REFERENCES player_characters (id),
            FOREIGN KEY (character2_id) REFERENCES player_characters (id),
            FOREIGN KEY (character3_id) REFERENCES player_characters (id),
            FOREIGN KEY (character4_id) REFERENCES player_characters (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS battles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            battle_type TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Verificar se já existem dados
    cursor.execute('SELECT COUNT(*) FROM characters')
    if cursor.fetchone()[0] == 0:
        # Inserir personagens iniciais
        initial_characters = [
            ('Guerreiro', 1, 100, 15, 10, 8, '/static/char_1.png', '["Ataque Básico"]', '[]'),
            ('Mago', 2, 80, 20, 5, 12, '/static/char_2.png', '["Ataque Básico", "Defesa"]', '["Resistência Básica"]'),
            ('Arqueiro', 2, 90, 18, 8, 15, '/static/char_3.png', '["Ataque Básico", "Defesa"]', '["Resistência Básica"]'),
            ('Paladino', 3, 120, 16, 15, 10, '/static/char_4.png', '["Ataque Básico", "Defesa", "Ataque Especial"]', '["Resistência Básica", "Regeneração"]'),
            ('Bruxo', 3, 85, 25, 6, 13, '/static/char_5.png', '["Ataque Básico", "Defesa", "Ataque Especial"]', '["Resistência Básica", "Regeneração"]'),
            ('Cavaleiro', 4, 140, 18, 18, 9, '/static/char_6.png', '["Ataque Básico", "Defesa", "Ataque Especial", "Cura"]', '["Resistência Básica", "Regeneração", "Crítico"]'),
            ('Feiticeiro', 4, 95, 30, 8, 14, '/static/char_7.png', '["Ataque Básico", "Defesa", "Ataque Especial", "Cura"]', '["Resistência Básica", "Regeneração", "Crítico"]'),
            ('Herói Lendário', 5, 200, 25, 20, 16, '/static/char_8.png', '["Ataque Básico", "Defesa", "Ataque Especial", "Cura", "Ultimate"]', '["Resistência Básica", "Regeneração", "Crítico", "Imunidade"]')
        ]
        
        for char in initial_characters:
            cursor.execute('''
                INSERT INTO characters (name, rarity, hp, attack, defense, speed, image_url, active_skills, passive_skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', char)
        
        # Inserir equipamentos iniciais
        initial_equipment = [
            ('Espada de Ferro', 'weapon', 1, 0, 5, 0, 0),
            ('Armadura de Couro', 'armor', 1, 0, 0, 3, 0),
            ('Anel de Força', 'accessory', 1, 0, 2, 0, 0),
            ('Espada de Aço', 'weapon', 2, 0, 8, 0, 0),
            ('Armadura de Aço', 'armor', 2, 0, 0, 6, 0),
            ('Anel de Poder', 'accessory', 2, 0, 4, 0, 0)
        ]
        
        for equip in initial_equipment:
            cursor.execute('''
                INSERT INTO equipment (name, type, rarity, hp_bonus, attack_bonus, defense_bonus, speed_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', equip)
    
    conn.commit()
    conn.close()

def get_db():
    """Obtém conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_enemy_stats(base_character, phase):
    """Calcula os stats do inimigo baseado na fase"""
    # Fórmula de escalonamento: stats aumentam 10% a cada 10 fases
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

def get_enemies_for_phase(phase, battle_type='story'):
    """Obtém inimigos para uma fase específica"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Buscar personagens base para criar inimigos
    cursor.execute('SELECT * FROM characters ORDER BY rarity, id')
    base_characters = cursor.fetchall()
    conn.close()
    
    enemies = []
    
    if battle_type == 'story':
        # Para história, usar personagens baseados na fase
        if phase <= 10:
            # Fases 1-10: Guerreiros e Magos básicos
            selected_chars = [base_characters[0], base_characters[1]]  # Guerreiro, Mago
        elif phase <= 20:
            # Fases 11-20: Adicionar Arqueiro
            selected_chars = [base_characters[0], base_characters[1], base_characters[2]]  # Guerreiro, Mago, Arqueiro
        elif phase <= 30:
            # Fases 21-30: Adicionar Paladino
            selected_chars = [base_characters[0], base_characters[1], base_characters[2], base_characters[3]]  # Guerreiro, Mago, Arqueiro, Paladino
        else:
            # Fases 31+: Todos os personagens
            selected_chars = base_characters[:6]  # Primeiros 6 personagens
        
        # Selecionar 2 inimigos aleatórios
        num_enemies = min(2, len(selected_chars))
        selected_enemies = random.sample(selected_chars, num_enemies)
        
        for i, base_char in enumerate(selected_enemies):
            enemy = calculate_enemy_stats(base_char, phase)
            enemy['id'] = 1000 + phase * 10 + i  # ID único baseado na fase
            enemies.append(enemy)
    
    elif battle_type == 'arena':
        # Para arena, usar personagens mais fortes
        if phase <= 5:
            selected_chars = [base_characters[3], base_characters[4]]  # Paladino, Bruxo
        else:
            selected_chars = [base_characters[5], base_characters[6]]  # Cavaleiro, Feiticeiro
        
        for i, base_char in enumerate(selected_chars):
            enemy = calculate_enemy_stats(base_char, phase)
            enemy['id'] = 2000 + phase * 10 + i  # ID único baseado na fase
            enemies.append(enemy)
    
    return enemies

def select_enemy_target(enemy, player_team, battle_type='story'):
    """Seleciona o alvo do inimigo"""
    alive_players = [p for p in player_team if p['status']['is_alive']]
    
    if not alive_players:
        return None
    
    # Lógica de seleção de alvo baseada no tipo de batalha
    if battle_type == 'story':
        # Para história: atacar o personagem com menos HP (mais vulnerável)
        target = min(alive_players, key=lambda p: p['status']['current_hp'])
    elif battle_type == 'arena':
        # Para arena: atacar aleatoriamente (mais estratégico)
        target = random.choice(alive_players)
    else:
        # Padrão: aleatório
        target = random.choice(alive_players)
    
    return target

@app.route('/')
def index():
    return render_template('index.html')

# Rotas da API
@app.route('/api/characters', methods=['GET'])
def get_characters():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM characters')
    characters = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': c['id'],
        'name': c['name'],
        'rarity': c['rarity'],
        'hp': c['hp'],
        'attack': c['attack'],
        'defense': c['defense'],
        'speed': c['speed'],
        'image_url': c['image_url'],
        'active_skills': json.loads(c['active_skills']) if c['active_skills'] else [],
        'passive_skills': json.loads(c['passive_skills']) if c['passive_skills'] else []
    } for c in characters])

@app.route('/api/player-characters', methods=['GET'])
def get_player_characters():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pc.*, c.name, c.rarity, c.hp as base_hp, c.attack as base_attack, 
               c.defense as base_defense, c.speed as base_speed, c.image_url
        FROM player_characters pc
        JOIN characters c ON pc.character_id = c.id
    ''')
    player_chars = cursor.fetchall()
    conn.close()
    
    result = []
    for pc in player_chars:
        result.append({
            'id': pc['id'],
            'character_id': pc['character_id'],
            'name': pc['name'],
            'rarity': pc['rarity'],
            'level': pc['level'],
            'exp': pc['exp'],
            'hp': pc['base_hp'] + pc['level'] * 10,
            'attack': pc['base_attack'] + pc['level'] * 2,
            'defense': pc['base_defense'] + pc['level'] * 1,
            'speed': pc['base_speed'] + pc['level'] * 1,
            'image_url': pc['image_url'],
            'equipment': {
                'weapon': pc['equipment_weapon'],
                'armor': pc['equipment_armor'],
                'accessory': pc['equipment_accessory']
            }
        })
    return jsonify(result)

@app.route('/api/equipment', methods=['GET'])
def get_equipment():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipment')
    equipment = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': e['id'],
        'name': e['name'],
        'type': e['type'],
        'rarity': e['rarity'],
        'hp_bonus': e['hp_bonus'],
        'attack_bonus': e['attack_bonus'],
        'defense_bonus': e['defense_bonus'],
        'speed_bonus': e['speed_bonus']
    } for e in equipment])

@app.route('/api/teams', methods=['GET'])
def get_teams():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teams')
    teams = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': t['id'],
        'name': t['name'],
        'characters': [t['character1_id'], t['character2_id'], t['character3_id'], t['character4_id']],
        'is_main_team': bool(t['is_main_team'])
    } for t in teams])

@app.route('/api/teams', methods=['POST'])
def create_team():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    # Se for main team, desmarcar outros
    if data.get('is_main_team', False):
        cursor.execute('UPDATE teams SET is_main_team = FALSE')
    
    cursor.execute('''
        INSERT INTO teams (name, character1_id, character2_id, character3_id, character4_id, is_main_team)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data.get('character1_id'),
        data.get('character2_id'),
        data.get('character3_id'),
        data.get('character4_id'),
        data.get('is_main_team', False)
    ))
    
    team_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': team_id, 'message': 'Time criado com sucesso'})

@app.route('/api/battle/start', methods=['POST'])
def start_battle():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO battles (battle_type) VALUES (?)', (data['type'],))
    battle_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Buscar equipe do jogador (main team)
    conn = get_db()
    cursor = conn.cursor()
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
                        'id': pc['id'],
                        'name': pc['name'],
                        'rarity': pc['rarity'],
                        'hp': pc['base_hp'] + pc['level'] * 10,
                        'max_hp': pc['base_hp'] + pc['level'] * 10,
                        'attack': pc['base_attack'] + pc['level'] * 2,
                        'defense': pc['base_defense'] + pc['level'] * 1,
                        'speed': pc['base_speed'] + pc['level'] * 1,
                        'image_url': pc['image_url'] or f'/static/char_{pc["character_id"]}.png',
                        'type': 'player',
                        'skills': json.loads(pc['active_skills']) if pc['active_skills'] else ["Ataque Básico"],
                        'status': {
                            'is_alive': True,
                            'is_conscious': True,
                            'current_hp': pc['base_hp'] + pc['level'] * 10,
                            'buffs': [],
                            'debuffs': []
                        }
                    })
    conn.close()

    # Obter inimigos baseados na fase
    phase = data.get('phase', 1)
    enemies = get_enemies_for_phase(phase, data['type'])

    # Criar ordem de ação baseada em velocidade
    all_combatants = player_team + enemies
    action_order = sorted(all_combatants, key=lambda c: -c['speed'])
    
    # Adicionar informações de ordem
    for idx, c in enumerate(action_order):
        c['order_idx'] = idx
        c['has_acted_this_turn'] = False

    # Salvar estado da batalha
    BATTLES[battle_id] = {
        'player_team': player_team,
        'enemies': enemies,
        'action_order': action_order,
        'turn_idx': 0,
        'battle_type': data['type'],
        'status': 'active',
        'winner': None,
        'phase': phase,
        'current_round': 1
    }

    return jsonify({
        'battle_id': battle_id,
        'enemies': enemies,
        'player_team': player_team,
        'action_order': action_order,
        'turn_idx': 0,
        'message': 'Batalha iniciada'
    })

@app.route('/api/battle/<int:battle_id>/state', methods=['GET'])
def get_battle_state(battle_id):
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

def update_combatant_status(combatant, damage=0, heal=0, status_effect=None):
    """Atualiza o status de um combatente"""
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

def get_next_actor(battle):
    """Obtém o próximo ator válido na ordem de ação"""
    order = battle['action_order']
    current_idx = battle['turn_idx']
    
    # Procurar próximo ator vivo e consciente que ainda não agiu neste round
    for i in range(len(order)):
        idx = (current_idx + i) % len(order)
        combatant = order[idx]
        
        if (combatant['status']['is_alive'] and 
            combatant['status']['is_conscious'] and 
            not combatant['has_acted_this_turn']):
            return idx
    
    return None

def advance_turn(battle):
    """Avança para o próximo turno"""
    order = battle['action_order']
    current_idx = battle['turn_idx']
    
    # Marcar que o ator atual já agiu
    if current_idx < len(order):
        order[current_idx]['has_acted_this_turn'] = True
    
    # Verificar se todos agiram neste round
    alive_combatants = [c for c in order if c['status']['is_alive'] and c['status']['is_conscious']]
    all_acted = all(c['has_acted_this_turn'] for c in alive_combatants)
    
    if all_acted and len(alive_combatants) > 0:
        # Novo round - resetar flags
        battle['current_round'] += 1
        for c in order:
            c['has_acted_this_turn'] = False
        print(f"Novo round iniciado: {battle['current_round']}")
    
    # Próximo ator
    next_idx = get_next_actor(battle)
    if next_idx is not None:
        battle['turn_idx'] = next_idx
        print(f"Próximo ator: {order[next_idx]['name']} (índice {next_idx})")
    else:
        # Ninguém pode agir - batalha acabou
        battle['status'] = 'finished'
        print("Ninguém pode agir - batalha finalizada")

@app.route('/api/battle/<int:battle_id>/action', methods=['POST'])
def battle_action(battle_id):
    data = request.json
    battle = BATTLES.get(battle_id)
    if not battle or battle['status'] != 'active':
        return jsonify({'error': 'Batalha não encontrada ou já finalizada'}), 400

    order = battle['action_order']
    turn_idx = battle['turn_idx']
    current = order[turn_idx]

    # Verificar se o ator atual pode agir
    if not current['status']['is_alive'] or not current['status']['is_conscious']:
        advance_turn(battle)
        return jsonify({'message': f'{current["name"]} não pode agir.', 'turn_idx': battle['turn_idx'], 'action_order': order, 'status': battle['status']})

    # Verificar se já agiu neste round
    if current['has_acted_this_turn']:
        advance_turn(battle)
        return jsonify({'message': f'{current["name"]} já agiu neste round.', 'turn_idx': battle['turn_idx'], 'action_order': order, 'status': battle['status']})

    # Se for player, processa ação recebida
    if current['type'] == 'player':
        action = data.get('action', 'Ataque Básico')
        target_id = data.get('target_id')
        
        # Encontrar alvo
        target = None
        if action in ['Ataque Básico', 'Ataque Especial']:
            target = next((e for e in battle['enemies'] if e['id'] == target_id and e['status']['is_alive']), None)
        elif action == 'Cura':
            target = next((p for p in battle['player_team'] if p['id'] == target_id and p['status']['is_alive']), None)
        
        if not target:
            return jsonify({'error': 'Alvo inválido'}), 400
        
        # Calcular dano/cura
        if action == 'Ataque Especial' and 'Ataque Especial' in current['skills']:
            damage = max(0, int(current['attack'] * 1.5) - target['defense'])
            update_combatant_status(target, damage=damage)
            msg = f'{current["name"]} usou {action} em {target["name"]} causando {damage} de dano.'
        elif action == 'Ataque Básico':
            damage = max(0, current['attack'] - target['defense'])
            update_combatant_status(target, damage=damage)
            msg = f'{current["name"]} usou {action} em {target["name"]} causando {damage} de dano.'
        elif action == 'Cura' and 'Cura' in current['skills']:
            heal = int(current['attack'] * 0.8)
            update_combatant_status(target, heal=heal)
            msg = f'{current["name"]} curou {target["name"]} em {heal} HP.'
        else:
            return jsonify({'error': 'Ação inválida'}), 400
    
    # Se for inimigo, executar ação
    else:
        # Selecionar alvo
        target = select_enemy_target(current, battle['player_team'], battle['battle_type'])
        if not target:
            battle['status'] = 'finished'
            battle['winner'] = 'enemy'
            return jsonify({'message': 'Derrota! Todos os personagens foram derrotados.', 'winner': 'enemy', 'status': 'finished'})
        
        # Alternar entre ataque básico e especial
        skill_idx = current.get('next_enemy_skill', 0)
        available_skills = current['skills']
        
        if len(available_skills) >= 2:
            # Alternar entre primeiro e segundo skill
            action = available_skills[skill_idx % 2]
        else:
            # Se só tem um skill, usar sempre
            action = available_skills[0]
        
        # Calcular dano
        if action == 'Ataque Especial':
            damage = max(0, int(current['attack'] * 1.5) - target['defense'])
        else:
            damage = max(0, current['attack'] - target['defense'])
        
        update_combatant_status(target, damage=damage)
        current['next_enemy_skill'] = (skill_idx + 1) % len(available_skills)
        msg = f'{current["name"]} usou {action} em {target["name"]} causando {damage} de dano.'

    # Verificar condições de vitória/derrota
    alive_enemies = [e for e in battle['enemies'] if e['status']['is_alive']]
    alive_players = [p for p in battle['player_team'] if p['status']['is_alive']]
    
    if not alive_enemies:
        battle['status'] = 'finished'
        battle['winner'] = 'player'
        # Liberar próxima fase se for história
        if battle['battle_type'] == 'story':
            phase = battle.get('phase', 1)
            if USER_PROGRESS['story'] <= phase:
                USER_PROGRESS['story'] = phase + 1
        return jsonify({
            'message': 'Vitória! Todos os inimigos derrotados.', 
            'winner': 'player', 
            'status': 'finished',
            'action_order': order
        })
    
    if not alive_players:
        battle['status'] = 'finished'
        battle['winner'] = 'enemy'
        return jsonify({
            'message': 'Derrota! Todos os personagens foram derrotados.', 
            'winner': 'enemy', 
            'status': 'finished',
            'action_order': order
        })
    
    # Avançar turno
    advance_turn(battle)
    
    return jsonify({
        'message': msg, 
        'turn_idx': battle['turn_idx'], 
        'action_order': order, 
        'status': battle['status'],
        'current_actor': order[battle['turn_idx']] if battle['turn_idx'] < len(order) else None,
        'current_round': battle.get('current_round', 1)
    })

@app.route('/api/battle/<int:battle_id>/victory', methods=['GET'])
def battle_victory(battle_id):
    battle = BATTLES.get(battle_id)
    if not battle or battle['status'] != 'finished' or battle['winner'] != 'player':
        return jsonify({'error': 'Vitória não encontrada'}), 400
    return jsonify({
        'message': 'Vitória!', 
        'phase': battle.get('phase', 1), 
        'next_phase': battle.get('phase', 1) + 1, 
        'user_progress': USER_PROGRESS['story']
    })

@app.route('/api/story/progress', methods=['GET'])
def get_story_progress():
    return jsonify({'max_phase': USER_PROGRESS['story']})

@app.route('/api/gacha/pull', methods=['POST'])
def gacha_pull():
    # Simular pull do gacha
    rarity_weights = {1: 70, 2: 20, 3: 8, 4: 1.5, 5: 0.5}
    rarity = random.choices(list(rarity_weights.keys()), weights=list(rarity_weights.values()))[0]
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Selecionar personagem da raridade
    cursor.execute('SELECT * FROM characters WHERE rarity = ?', (rarity,))
    characters = cursor.fetchall()
    
    if characters:
        character = random.choice(characters)
        
        # Adicionar ao inventário do jogador
        cursor.execute('''
            INSERT INTO player_characters (character_id)
            VALUES (?)
        ''', (character['id'],))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'character': {
                'id': character['id'],
                'name': character['name'],
                'rarity': character['rarity'],
                'hp': character['hp'],
                'attack': character['attack'],
                'defense': character['defense'],
                'speed': character['speed']
            },
            'message': f'Você obteve {character["name"]} ({rarity}★)!'
        })
    
    conn.close()
    return jsonify({'error': 'Nenhum personagem encontrado'})

if __name__ == '__main__':
    # Inicializar banco de dados
    init_db()
    print("Banco de dados inicializado com sucesso!")
    print("Servidor rodando em: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 