import io

from flask import Flask, request
from flask_mqtt import Mqtt
from PIL import Image

from model import Model
from logger import setup_logger

app = Flask("Yolo V5 Rest API")
app.config.from_object('config.Config')

mqtt = Mqtt()
mqtt.init_app(app)

DETECTION_URL = "/api/v1/yolo/object-detection"
logger = setup_logger()
model = Model(mqtt, logger)


@app.route("/api/v1/health", methods=["GET", "POST"])
def health():
    return {"health": "Running", "success": True}


@app.route(DETECTION_URL, methods=["POST"])
def predict():
    if request.method != "POST":
        return

    if request.files.get("image"):
        im_file = request.files["image"]
        im_bytes = im_file.read()
        im = Image.open(io.BytesIO(im_bytes))
        uuid = request.form.get('uuid')
        logger.info(f"Received detection request with id {uuid}")
        model(im, size=1280, uuid=uuid)
        return {"success": True}, 200

    else:
        return {"error": "No enough data", "msg": "Image was not attached."}

