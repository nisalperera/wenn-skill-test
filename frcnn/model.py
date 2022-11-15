import json
import os
from threading import Thread

import numpy as np
import torch
from PIL import Image
from torchvision.models.detection.faster_rcnn import fasterrcnn_resnet50_fpn
from torchvision.transforms import Compose, Normalize, ToTensor

from config import Config

torch.set_printoptions(sci_mode=False)


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
        self.model = fasterrcnn_resnet50_fpn(pretrained=True, pretrained_backbone=True).eval()
        self.transform = Compose([ToTensor(), Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
        self.mqtt_client = client
        self.logger = logger

    def __call__(self, im: Image.Image, uuid: str = '') -> bool:
        thread = Thread(target=self.__predict, args=[im, uuid])
        thread.daemon = True
        thread.start()
        return True

    def __predict(self, im: Image.Image, uuid: str = ''):
        @self.mqtt_client.on_publish()
        def handle_publish(client, userdata, mid):
            self.logger.info('Published message with mid {}.'.format(mid))

        with torch.no_grad():
            transformed_img = self.__prepocess(im)
            results = self.model([transformed_img])[0]
            self.logger.debug(results)
            boxes = results['boxes']
            labels = results['labels']
            scores = results['scores']
            boxes[:, 0] = boxes[:, 0] / im.width
            boxes[:, 1] = boxes[:, 1] / im.height
            boxes[:, 2] = boxes[:, 2] / im.width
            boxes[:, 3] = boxes[:, 3] / im.height

            result = {
                "uuid": uuid,
                "source": "frcnn",
                "result": {
                    "boxes": boxes.tolist(),
                    "labels": labels.tolist(),
                    "scores": scores.tolist()
                }
            }
            self.mqtt_client.publish("wenn/detections", json.dumps(result))
            self.logger.info(f"Detection Results from frcnn model published...")

            file_path = os.path.join(Config.MEDIA_FOLDER, uuid)

            if not os.path.exists(file_path):
                os.makedirs(file_path)

            with open(os.path.join(file_path, "results.json"), 'w+') as res:
                json.dump(result, res)

    def __prepocess(self, im: Image.Image):
        # np_sample_image = np.array(im)

        return self.transform(np.array(im))
