
FROM python:3.10-alpine
WORKDIR /usr/app/
RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt
RUN apk add py3-lxml

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r ./requirements.txt

COPY SmartMeterVKW.py ./
COPY config/config.json ./config/

ENTRYPOINT [ "python3","-u","./SmartMeterVKW.py"]