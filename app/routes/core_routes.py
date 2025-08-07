from flask import Blueprint, render_template, jsonify

core_bp = Blueprint('core', __name__)


@core_bp.route('/')
def index():
    return render_template('index.html')


@core_bp.route('/health')
def health():
    return jsonify({'status': 'ok'})
