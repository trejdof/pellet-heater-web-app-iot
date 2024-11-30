from flask import Flask, render_template, jsonify, request
import json
import os

# Environment variables
DATA_FOLDER = os.getenv("DATA_FOLDER", "data")  # Default to "data" if not set
WEEK_CONFIG_PATH = os.getenv("WEEK_CONFIG_PATH", os.path.join(DATA_FOLDER, "week_config.json"))
CURRENT_CONFIG_PATH = os.getenv("CURRENT_CONFIG_PATH", os.path.join(DATA_FOLDER, "current_config.json"))
LAST_TEMPERATURE_PATH = os.getenv("LAST_TEMPERATURE_PATH", os.path.join(DATA_FOLDER, "last_temperature_reading.json"))
STOVE_STATUS_PATH = os.getenv("STOVE_STATUS_PATH", os.path.join(DATA_FOLDER, "stove_status.json"))


app = Flask(__name__)

# Helper functions
def load_json(file_path, default=None):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return default if default is not None else {}

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def generate_new_config_name(existing_configs):
    return f"Konfiguracija_{len(existing_configs) + 1}"

# Routes
@app.route('/')
def home():
    configs = load_json(WEEK_CONFIG_PATH, [])
    return render_template('dashboard.html', configurations=configs)

@app.route('/config/<name>')
def view_config(name):
    configs = load_json(WEEK_CONFIG_PATH, [])
    config = next((c for c in configs if c['name'] == name), None)
    if config is None:
        return "Configuration not found", 404
    return render_template('config_page.html', config=config)

@app.route('/api/configurations', methods=['GET'])
def configurations():
    configs = load_json(WEEK_CONFIG_PATH, [])
    return jsonify(configs)

@app.route('/api/configurations', methods=['POST'])
def add_configuration():
    configs = load_json(WEEK_CONFIG_PATH, [])
    new_name = generate_new_config_name(configs)
    new_config = {"name": new_name, "days": []}
    configs.append(new_config)
    save_json(WEEK_CONFIG_PATH, configs)
    return jsonify(new_config), 201

@app.route('/api/configurations/<name>', methods=['POST'])
def save_configuration(name):
    configs = load_json(WEEK_CONFIG_PATH, [])
    config = next((c for c in configs if c['name'] == name), None)

    if not config:
        return jsonify({"message": "Configuration not found"}), 404

    # Update the configuration with the new data
    updated_config = request.json
    config['days'] = updated_config

    # Save the updated configurations back to the file
    save_json(WEEK_CONFIG_PATH, configs)
    return jsonify({"message": "Configuration updated successfully"})

@app.route('/api/current-config', methods=['GET', 'POST'])
def current_config():
    # GET: Return the current configuration name
    if request.method == 'GET':
        data = load_json(CURRENT_CONFIG_PATH, {"name": "None"})
        return jsonify(data)

    # POST: Update the current configuration name
    elif request.method == 'POST':
        data = request.json
        save_json(CURRENT_CONFIG_PATH, data)
        return jsonify({"message": "Current configuration updated"})

@app.route('/api/last-temperature', methods=['GET'])
def last_temperature():
    data = load_json(LAST_TEMPERATURE_PATH, {"temperature": "N/A", "timestamp": "N/A"})
    return jsonify(data)

@app.route('/api/stove-status', methods=['GET'])
def stove_status():
    data = load_json(STOVE_STATUS_PATH, {"status": 0, "timestamp": "N/A"})  # Default to "Off" and no timestamp
    return jsonify(data)

@app.route('/api/configurations/<name>', methods=['GET'])
def get_configuration(name):
    configs = load_json(WEEK_CONFIG_PATH, [])
    config = next((c for c in configs if c['name'] == name), None)

    if not config:
        return jsonify({"message": "Configuration not found"}), 404

    return jsonify(config)


@app.context_processor
def inject_configurations():
    configs = load_json(WEEK_CONFIG_PATH, [])
    return {'configurations': configs}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
