from flask import Blueprint, jsonify
from ..db.init_db import get_db

equipment_bp = Blueprint('equipment', __name__)


@equipment_bp.route('/equipment', methods=['GET'])
def get_equipment():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipment')
    equipment = cursor.fetchall()
    conn.close()
    return jsonify([
        {
            'id': e['id'],
            'name': e['name'],
            'type': e['type'],
            'rarity': e['rarity'],
            'hp_bonus': e['hp_bonus'],
            'attack_bonus': e['attack_bonus'],
            'defense_bonus': e['defense_bonus'],
            'speed_bonus': e['speed_bonus']
        }
        for e in equipment
    ])
