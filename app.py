from flask import Flask, render_template, jsonify, request
import json
import os
import paho.mqtt.client as mqtt
import random
from datetime import datetime

# Environment variables
DATA_FOLDER = os.getenv("DATA_FOLDER", "data")  # Default to "data" if not set
WEEK_CONFIG_PATH = os.getenv("WEEK_CONFIG_PATH", os.path.join(DATA_FOLDER, "week_config.json"))
CURRENT_CONFIG_PATH = os.getenv("CURRENT_CONFIG_PATH", os.path.join(DATA_FOLDER, "current_config.json"))
LAST_TEMPERATURE_PATH = os.getenv("LAST_TEMPERATURE_PATH", os.path.join(DATA_FOLDER, "last_temperature_reading.json"))
STOVE_STATUS_PATH = os.getenv("STOVE_STATUS_PATH", os.path.join(DATA_FOLDER, "stove_status.json"))

# MQTT Configuration
MQTT_BROKER = "localhost"  # Set to Raspberry Pi's IP for external connections
MQTT_PORT = 1883
MQTT_TOPIC = "test/topic"
MQTT_USER = None           # Set your MQTT username (if using authentication)
MQTT_PASSWORD = None       # Set your MQTT password (if using authentication)

# Initialize Flask app
app = Flask(__name__)

# Initialize MQTT client
mqtt_client = mqtt.Client()

if MQTT_USER and MQTT_PASSWORD:
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# Callbacks for MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT broker")
        client.subscribe(MQTT_TOPIC)  # Subscribe to topic after successful connection
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed successfully, granted QoS: {granted_qos}")

def on_log(client, userdata, level, buf):
    print(f"MQTT log: {buf}")

def on_message(client, userdata, msg):
    # Decode the received message
    try:
        payload = json.loads(msg.payload.decode())  # Assuming the message is JSON
        topic = msg.topic

        # Check if it's the topic you're interested in
        if topic == MQTT_TOPIC:
            # Randomize the temperature for testing purposes
            temperature = round(random.uniform(18.0, 25.0), 1)

            # Use the current time as the timestamp
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # Update the JSON file with the randomized data
            save_json(LAST_TEMPERATURE_PATH, {"temperature": temperature, "timestamp": timestamp})
            print(f"Updated {LAST_TEMPERATURE_PATH} with randomized temperature: {temperature} and timestamp: {timestamp}")

        else:
            print(f"Received message on unhandled topic {topic}: {payload}")

    except json.JSONDecodeError as e:
        print(f"Failed to decode message payload: {msg.payload.decode()} - Error: {e}")

# Assign MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe
mqtt_client.on_log = on_log

# Connect to MQTT broker and start loop
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.enable_logger()
mqtt_client.loop_start()

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
    # Load the last temperature reading from the JSON file
    data = load_json(LAST_TEMPERATURE_PATH, {"temperature": "N/A", "timestamp": "N/A"})
    
    # Prepare the message to publish
    message = {
        "temperature": data.get("temperature", "N/A"),
        "timestamp": data.get("timestamp", "N/A")
    }

    # Publish the message to the MQTT topic
    mqtt_client.publish(MQTT_TOPIC, json.dumps(message))

    # Return the JSON data as the API response
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

@app.route('/publish', methods=['POST'])
def publish_message():
    """Route to publish a message to MQTT"""
    data = request.json
    topic = data.get("topic", MQTT_TOPIC)
    message = data.get("message", "Hello from Flask!")
    mqtt_client.publish(topic, message)
    return jsonify({"status": "Message published!"})

@app.context_processor
def inject_configurations():
    configs = load_json(WEEK_CONFIG_PATH, [])
    return {'configurations': configs}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
