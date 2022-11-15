import os
import requests


def send_request(request_files, request_data, url):
    if "yolo" in url:
        url = f"http://{os.getenv('YOLO', 'localhost:5000')}{url}"

    elif "frcnn" in url:
        url = f"http://{os.getenv('FRCNN', 'localhost:6000')}{url}"

    requests.post(url, files=request_files, data=request_data)
