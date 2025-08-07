import sqlite3
import json

DATABASE = 'gacha_game.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

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

    cursor.execute('SELECT COUNT(*) FROM characters')
    if cursor.fetchone()[0] == 0:
        initial_characters = [
            ('Guerreiro', 1, 100, 15, 10, 8, '/static/char_1.png', json.dumps(["Ataque Básico"]), json.dumps([])),
            ('Mago', 2, 80, 20, 5, 12, '/static/char_2.png', json.dumps(["Ataque Básico", "Defesa"]), json.dumps(["Resistência Básica"])),
            ('Arqueiro', 2, 90, 18, 8, 15, '/static/char_3.png', json.dumps(["Ataque Básico", "Defesa"]), json.dumps(["Resistência Básica"])),
            ('Paladino', 3, 120, 16, 15, 10, '/static/char_4.png', json.dumps(["Ataque Básico", "Defesa", "Ataque Especial"]), json.dumps(["Resistência Básica", "Regeneração"])),
            ('Bruxo', 3, 85, 25, 6, 13, '/static/char_5.png', json.dumps(["Ataque Básico", "Defesa", "Ataque Especial"]), json.dumps(["Resistência Básica", "Regeneração"])),
            ('Cavaleiro', 4, 140, 18, 18, 9, '/static/char_6.png', json.dumps(["Ataque Básico", "Defesa", "Ataque Especial", "Cura"]), json.dumps(["Resistência Básica", "Regeneração", "Crítico"])),
            ('Feiticeiro', 4, 95, 30, 8, 14, '/static/char_7.png', json.dumps(["Ataque Básico", "Defesa", "Ataque Especial", "Cura"]), json.dumps(["Resistência Básica", "Regeneração", "Crítico"])),
            ('Herói Lendário', 5, 200, 25, 20, 16, '/static/char_8.png', json.dumps(["Ataque Básico", "Defesa", "Ataque Especial", "Cura", "Ultimate"]), json.dumps(["Resistência Básica", "Regeneração", "Crítico", "Imunidade"]))
        ]
        cursor.executemany('''
            INSERT INTO characters (name, rarity, hp, attack, defense, speed, image_url, active_skills, passive_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', initial_characters)

        initial_equipment = [
            ('Espada de Ferro', 'weapon', 1, 0, 5, 0, 0),
            ('Armadura de Couro', 'armor', 1, 0, 0, 3, 0),
            ('Anel de Força', 'accessory', 1, 0, 2, 0, 0),
            ('Espada de Aço', 'weapon', 2, 0, 8, 0, 0),
            ('Armadura de Aço', 'armor', 2, 0, 0, 6, 0),
            ('Anel de Poder', 'accessory', 2, 0, 4, 0, 0)
        ]
        cursor.executemany('''
            INSERT INTO equipment (name, type, rarity, hp_bonus, attack_bonus, defense_bonus, speed_bonus)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', initial_equipment)

    conn.commit()
    conn.close()
