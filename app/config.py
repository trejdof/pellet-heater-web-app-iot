import os

class Config:
    DATA_FOLDER = os.getenv("DATA_FOLDER", "data")
    WEEK_CONFIG_PATH = os.getenv("WEEK_CONFIG_PATH", os.path.join(DATA_FOLDER, "week_config.json"))
    CURRENT_CONFIG_PATH = os.getenv("CURRENT_CONFIG_PATH", os.path.join(DATA_FOLDER, "current_config.json"))
    LAST_TEMPERATURE_PATH = os.getenv("LAST_TEMPERATURE_PATH", os.path.join(DATA_FOLDER, "last_temperature_reading.json"))
    STOVE_STATUS_PATH = os.getenv("STOVE_STATUS_PATH", os.path.join(DATA_FOLDER, "stove_status.json"))
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
