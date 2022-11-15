import json
from pathlib import Path

import yaml
import os.path
from uuid import uuid4

from PIL import Image, ImageDraw
from flask_uuid import FlaskUUID

from threading import Thread
from flask import Flask, request
from flask_mqtt import Mqtt
from detection import send_request
from subscribe import subscribe
from config import Config
from logger import setup_logger

app = Flask("Image uploader Rest API")

app.config.from_object('config.Config')

flask_uuid = FlaskUUID()
flask_uuid.init_app(app)

mqtt = Mqtt()
mqtt.init_app(app)

logger = setup_logger()

logger.info("Subscribe to topic wenn/results...")
subscribe("wenn/results", mqtt)


@app.route("/api/v1/health", methods=["GET", "POST"])
def health():
    return {"health": "Running", "success": True}


@app.route("/api/v1/upload", methods=["POST"])
def detect():
    if request.method != "POST":
        return

    if request.files.get("image"):
        form_data = request.form.to_dict()
        form_data["uuid"] = str(uuid4())

        images = request.files.getlist('image')
        files = []
        for image in images:
            files.append(("image", (image.filename, image.read(), image.content_type)))

        image = Image.open(images[0])
        save_image(image, form_data["uuid"])
        yolo = Thread(target=send_request, args=[files, form_data, "/api/v1/yolo/object-detection"], daemon=True)
        frcnn = Thread(target=send_request, args=[files, form_data, "/api/v1/frcnn/object-detection"], daemon=True)

        yolo.start()
        frcnn.start()
        
        return {"success": True}, 200

    else:
        return {"error": "No enough data", "msg": "Image was not attached."}


@mqtt.on_message()
def handle_message(client, userdata, message):
    payload = json.loads(message.payload)
    image = read_image(payload['uuid'])

    imaged = ImageDraw.Draw(image)
    classes = open_yaml("media/classes.yml")
    for box, label, score in zip(payload['boxes'], payload['labels'], payload['scores']):
        box[0] = box[0] * image.width
        box[1] = box[1] * image.height
        box[2] = box[2] * image.width
        box[3] = box[3] * image.height
        imaged.rectangle(box, outline="red")
        imaged.text(box[:2], f"{classes[int(label)]}: {score}")

    save_image(image, payload['uuid'], 'result.jpeg')


def open_yaml(filepath: str):
    return yaml.safe_load(Path(filepath).read_text())


def save_image(image: Image.Image, uuid: str, name: str = None):
    filepath = os.path.join(Config.MEDIA_FOLDER, uuid)

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if name:
        image.save(os.path.join(filepath, name))
    else:
        image.save(os.path.join(filepath, 'submit.jpeg'))


def read_image(uuid: str):
    filepath = os.path.join(Config.MEDIA_FOLDER, uuid, 'submit.jpeg')
    return Image.open(filepath)
