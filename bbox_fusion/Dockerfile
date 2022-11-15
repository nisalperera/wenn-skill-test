FROM python:3.8.15

ENV DEBIAN_FRONTEND=noninteractive

# Install linux packages
#RUN apt update && apt install --no-install-recommends -y zip htop screen libgl1-mesa-glx
RUN apt update && apt install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    gcc \
    libgl1-mesa-glx \
    zip \
    htop \
    screen gunicorn

# Install pip packages
COPY requirements.txt .
RUN pip3 install --no-cache -r requirements.txt gunicorn

# Create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy contents
COPY . /usr/src/app/

# Set environment variables
ENV OMP_NUM_THREADS=8
