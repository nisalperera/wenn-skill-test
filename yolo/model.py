import json
import os.path

import numpy as np
import torch
from PIL import Image

from threading import Thread

from config import Config


class Singleton(type):
    def __init__(self, name, bases, dic):
        self.__single_instance = None
        super().__init__(name, bases, dic)

    def __call__(cls, *args, **kwargs):
        if cls.__single_instance:
            return cls.__single_instance
        single_obj = cls.__new__(cls)
        single_obj.__init__(*args, **kwargs)
        cls.__single_instance = single_obj
        return single_obj


class Model(metaclass=Singleton):

    def __init__(self, client, logger):
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5x", force_reload=True, trust_repo=True)
        self.mqtt_client = client
        self.logger = logger

    def __call__(self, im: Image.Image, size: int = 1280, uuid: str = '') -> bool:
        thread = Thread(target=self.__predict, args=[im, size, uuid])
        thread.daemon = True
        thread.start()
        return True

    def __predict(self, im: Image.Image, size: int = 1280, uuid: str = ''):
        @self.mqtt_client.on_publish()
        def handle_publish(client, userdata, mid):
            self.logger.info('Published message with mid {}.'.format(mid))

        results = self.model(im, size=size).pandas().xyxyn[0].to_numpy()
        results = results[np.where(results[:, 4] > 0.5)]
        self.logger.debug(results)
        result = {
            "uuid": uuid,
            "source": "yolo",
            "result": {
                "boxes": results[:, :4].tolist(),
                "labels": results[:, 5].tolist(),
                "scores": results[:, 4].tolist()
            }
        }
        self.mqtt_client.publish("wenn/detections", json.dumps(result))
        self.logger.info(f"Detection Results from yolo model published...")

        file_path = os.path.join(Config.MEDIA_FOLDER, uuid)

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        with open(os.path.join(file_path, "results.json"), 'w+') as res:
            json.dump(result, res)
