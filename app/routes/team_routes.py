from flask import Blueprint, jsonify, request
from ..db.init_db import get_db

teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/teams', methods=['GET'])
def get_teams():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teams')
    rows = cursor.fetchall()
    conn.close()
    teams = [{
        'id': t['id'],
        'name': t['name'],
        'characters': [t['character1_id'], t['character2_id'], t['character3_id'], t['character4_id']],
        'is_main_team': bool(t['is_main_team'])
    } for t in rows]
    return jsonify(teams)


@teams_bp.route('/teams', methods=['POST'])
def create_team():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    if data.get('is_main_team', False):
        cursor.execute('UPDATE teams SET is_main_team = FALSE')
    cursor.execute('''
        INSERT INTO teams (name, character1_id, character2_id, character3_id, character4_id, is_main_team)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data.get('character1_id'), data.get('character2_id'), data.get('character3_id'), data.get('character4_id'), data.get('is_main_team', False)
    ))
    team_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': team_id, 'message': 'Time criado com sucesso'})
