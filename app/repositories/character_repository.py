from typing import List, Dict, Any
from ..db.init_db import get_db


def list_characters() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM characters')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_player_characters() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pc.*, c.name, c.rarity, c.hp as base_hp, c.attack as base_attack, 
               c.defense as base_defense, c.speed as base_speed, c.image_url
        FROM player_characters pc
        JOIN characters c ON pc.character_id = c.id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
