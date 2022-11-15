import json
from random import randint

from paho.mqtt import client

from box_fusion import FusionClass
from config import Config
from logger import setup_logger

logger = setup_logger("bbox_fusion")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
    else:
        logger.error("Failed to connect, return code %d\n", rc)

    client.subscribe("wenn/detections")


def on_message(client, userdata, message):

    payload = json.loads(message.payload)
    fusion = FusionClass.getInstance(payload['uuid'], client, logger)
    yolo = payload['result'] if payload['source'] == 'yolo' else None
    frcnn = payload['result'] if payload['source'] == 'frcnn' else None

    if yolo:
        fusion.set_yolo_data(yolo)

    if frcnn:
        fusion.set_frcnn_data(frcnn)


def connect_mqtt():
    mqtt = client.Client(f'python-mqtt-{randint(0, 1000)}')
    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
        logger.info(f"Connecting to MQTT broker: {Config.MQTT_BROKER_URL}:{Config.MQTT_BROKER_PORT} with username and password")
        mqtt.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
    else:
        logger.info(f"Connecting to MQTT broker: {Config.MQTT_BROKER_URL}:{Config.MQTT_BROKER_PORT}")

    mqtt.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT)

    return mqtt


def run():
    client = connect_mqtt()
    client.loop_forever()


if __name__ == "__main__":
    run()
