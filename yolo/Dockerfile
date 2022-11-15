FROM python:3.8.15

ENV DEBIAN_FRONTEND=noninteractive

# Downloads to user config dir
ADD https://ultralytics.com/assets/Arial.ttf https://ultralytics.com/assets/Arial.Unicode.ttf /root/.config/Ultralytics/

# Install linux packages
RUN apt update && apt install --no-install-recommends -y zip htop screen libgl1-mesa-glx gunicorn git

# Install pip packages
COPY requirements.txt .
RUN pip3 install --no-cache -r requirements.txt
RUN pip3 install --no-cache torch==1.12.1+cpu torchvision==0.13.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy contents
COPY . /usr/src/app/

# Clone YOLOv5 repo
# RUN git clone https://github.com/ultralytics/yolov5.git

# Set environment variables
ENV OMP_NUM_THREADS=8
