from flask import Blueprint, render_template, jsonify, request, current_app
from app.utils import load_json, save_json, generate_new_config_name
from app.config import Config
import os

main = Blueprint('main', __name__)

import os

@main.route('/test')
def test_dashboard():
    template_dir = current_app.template_folder
    print(f"Flask is looking for templates in: {template_dir}")
    print(f"Absolute path of dashboard.html: {os.path.join(template_dir, 'dashboard.html')}")
    print(f"Does dashboard.html exist there? {os.path.exists(os.path.join(template_dir, 'dashboard.html'))}")
    
    try:
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error: {e}")
        return "Template not found, check logs.", 500
@main.route('/')
def home():
    configs = load_json(Config.WEEK_CONFIG_PATH, [])
    return render_template('dashboard.html', configurations=configs)

@main.route('/config/<name>')
def view_config(name):
    configs = load_json(Config.WEEK_CONFIG_PATH, [])
    config = next((c for c in configs if c['name'] == name), None)
    if config is None:
        return "Configuration not found", 404
    return render_template('config_page.html', config=config)

@main.route('/api/configurations', methods=['GET'])
def configurations():
    configs = load_json(Config.WEEK_CONFIG_PATH, [])
    return jsonify(configs)

@main.route('/api/configurations', methods=['POST'])
def add_configuration():
    configs = load_json(Config.WEEK_CONFIG_PATH, [])
    new_name = generate_new_config_name(configs)
    new_config = {"name": new_name, "days": []}
    configs.append(new_config)
    save_json(Config.WEEK_CONFIG_PATH, configs)
    return jsonify(new_config), 201

@main.route('/api/configurations/<name>', methods=['POST'])
def save_configuration(name):
    configs = load_json(Config.WEEK_CONFIG_PATH, [])
    config = next((c for c in configs if c['name'] == name), None)

    if not config:
        return jsonify({"message": "Configuration not found"}), 404

    updated_config = request.json
    config['days'] = updated_config
    save_json(Config.WEEK_CONFIG_PATH, configs)
    return jsonify({"message": "Configuration updated successfully"})

@main.route('/api/current-config', methods=['GET'])
def get_current_config():
    """
    Handle GET requests to fetch the current configuration.
    """
    data = load_json(Config.CURRENT_CONFIG_PATH, {"name": "None"})
    return jsonify(data)

@main.route('/api/current-config', methods=['POST'])
def post_current_config():
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Invalid request data"}), 400

    save_json(Config.CURRENT_CONFIG_PATH, data)

    # Debug: Log the saved data and the response
    print(f"Updated configuration: {data}")

    return jsonify({
        "message": "Current configuration updated",
        "name": data.get("name")
    })



@main.route('/api/last-temperature', methods=['GET'])
def last_temperature():
    data = load_json(Config.LAST_TEMPERATURE_PATH, {"temperature": "N/A", "timestamp": "N/A"})
    return jsonify(data)

@main.route('/api/stove-status', methods=['GET'])
def stove_status():
    data = load_json(Config.STOVE_STATUS_PATH, {"status": 0, "timestamp": "N/A"})
    return jsonify(data)

@main.route('/api/configurations/<name>', methods=['GET'])
def get_configuration(name):
    configs = load_json(Config.WEEK_CONFIG_PATH, [])
    config = next((c for c in configs if c['name'] == name), None)

    if not config:
        return jsonify({"message": "Configuration not found"}), 404

    return jsonify(config)
