import os


basedir = os.path.abspath(os.path.dirname(__file__))


class ConfigMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ConfigMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=ConfigMeta):
    STATIC_FOLDER = os.path.join(os.getcwd(), "static")
    MEDIA_FOLDER = os.path.join(os.getcwd(), "media")

    MQTT_BROKER_URL = os.getenv('MQTT_BROKER_URL', 'broker.hivemq.com')
    MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
    MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', '5'))
    MQTT_TLS_ENABLED = bool(os.getenv('MQTT_TLS_ENABLED', 0))
