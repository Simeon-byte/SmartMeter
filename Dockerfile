
FROM python:3.10-slim
WORKDIR /usr/app/
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r ./requirements.txt

COPY SmartMeterVKW.py .

RUN mkdir config

ENTRYPOINT [ "python3","-u","./SmartMeterVKW.py"]