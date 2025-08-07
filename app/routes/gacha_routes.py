from flask import Blueprint, jsonify
import random
from ..db.init_db import get_db

gacha_bp = Blueprint('gacha', __name__)


@gacha_bp.route('/gacha/pull', methods=['POST'])
def gacha_pull():
    rarity_weights = {1: 70, 2: 20, 3: 8, 4: 1.5, 5: 0.5}
    rarity = random.choices(list(rarity_weights.keys()), weights=list(rarity_weights.values()))[0]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM characters WHERE rarity = ?', (rarity,))
    characters = cursor.fetchall()
    if characters:
        character = random.choice(characters)
        cursor.execute('INSERT INTO player_characters (character_id) VALUES (?)', (character['id'],))
        conn.commit()
        conn.close()
        return jsonify({
            'character': {
                'id': character['id'], 'name': character['name'], 'rarity': character['rarity'],
                'hp': character['hp'], 'attack': character['attack'], 'defense': character['defense'], 'speed': character['speed']
            },
            'message': f'Você obteve {character["name"]} ({rarity}★)!'
        })
    conn.close()
    return jsonify({'error': 'Nenhum personagem encontrado'})
