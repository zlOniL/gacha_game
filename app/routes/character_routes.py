from flask import Blueprint, jsonify
from ..repositories.character_repository import list_characters, list_player_characters

characters_bp = Blueprint('characters', __name__)


@characters_bp.route('/characters', methods=['GET'])
def get_characters_route():
    return jsonify(list_characters())


@characters_bp.route('/player-characters', methods=['GET'])
def get_player_characters_route():
    rows = list_player_characters()
    result = []
    for pc in rows:
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
