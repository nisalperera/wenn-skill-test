import io

from flask_mqtt import Mqtt
from flask import Flask, request
from PIL import Image
from model import Model
from logger import setup_logger


app = Flask("Faster RCNN Rest API")
app.config.from_object('config.Config')

mqtt = Mqtt()
mqtt.init_app(app)

logger = setup_logger()

DETECTION_URL = "/api/v1/frcnn/object-detection"
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

        uuid = request.form.get('uuid', '')
        model(im, uuid=uuid)

        return {"success": True}, 200

    else:
        return {"error": "No enough data", "msg": "Image was not attached."}
