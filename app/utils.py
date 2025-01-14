import json
import os

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
