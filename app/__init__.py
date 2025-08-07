from flask import Flask
from flask_cors import CORS

from .db.init_db import init_db
from .routes.battle_routes import battle_bp
from .routes.core_routes import core_bp
from .routes.character_routes import characters_bp
from .routes.team_routes import teams_bp
from .routes.gacha_routes import gacha_bp
from .routes.equipment_routes import equipment_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder='../templates',  # usa templates na raiz do projeto
        static_folder='../static'       # usa static na raiz do projeto
    )
    CORS(app)

    # Inicializa banco de dados (schemas e seed)
    init_db()

    # Blueprints
    app.register_blueprint(core_bp)
    app.register_blueprint(characters_bp, url_prefix='/api')
    app.register_blueprint(teams_bp, url_prefix='/api')
    app.register_blueprint(battle_bp, url_prefix='/api')
    app.register_blueprint(gacha_bp, url_prefix='/api')
    app.register_blueprint(equipment_bp, url_prefix='/api')

    return app
