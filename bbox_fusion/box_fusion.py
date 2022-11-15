import json
import os

from ensemble_boxes import weighted_boxes_fusion

from config import Config


class FusionClass:
    __instance = {}

    @staticmethod
    def getInstance(u_id, mqtt_client, logger):
        """ Static access method. """
        if u_id not in FusionClass.__instance:
            FusionClass.__instance[u_id] = FusionClass(u_id, mqtt_client, logger)

        return FusionClass.__instance[u_id]

    def __init__(self, u_id, mqtt_client, logger):
        """ Virtually private constructor. """
        if u_id in FusionClass.__instance:
            raise Exception("This class is a singleton!")
        else:
            self.uid = u_id
            self.yolo = None
            self.frcnn = None
            self.mqtt_client = mqtt_client
            self.logger = logger

    def check_yolo_frcnn(self):
        return self.yolo is not None and self.frcnn is not None

    def set_yolo_data(self, yolo_data):
        self.yolo = yolo_data
        if self.check_yolo_frcnn():
            self.calculate_fusion()

    def set_frcnn_data(self, frcnn_data):
        self.frcnn = frcnn_data
        if self.check_yolo_frcnn():
            self.calculate_fusion()

    def calculate_fusion(self):
        self.logger.debug(f"UUID: {self.uid}")
        self.logger.debug(f"YOLO: {self.yolo}")
        self.logger.debug(f"FRCNN: {self.frcnn}")

        boxes_list = [self.yolo['boxes'], self.frcnn['boxes']]
        scores_list = [self.yolo['scores'], self.frcnn['scores']]
        labels_list = [self.yolo['labels'], self.frcnn['labels']]
        weights = [1, 2]

        iou_thr = 0.5
        skip_box_thr = 0.0001
        sigma = 0.1

        boxes, scores, labels = weighted_boxes_fusion(boxes_list, scores_list, labels_list, weights=weights,
                                                      iou_thr=iou_thr, skip_box_thr=skip_box_thr)

        fusion = {
            'uuid': self.uid,
            'boxes': boxes.tolist(),
            'scores': scores.tolist(),
            'labels': labels.tolist()
        }

        self.logger.debug(f"Fusion Result: {fusion}")

        self.mqtt_client.publish("wenn/results", json.dumps(fusion))
        self.logger.info(f"Fusion Result calculated and published...")

        file_path = os.path.join(Config.MEDIA_FOLDER, self.uid)

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        with open(os.path.join(file_path, "results.json"), 'w+') as res:
            json.dump(fusion, res)
