FROM python:3.11.5-bookworm

WORKDIR /app

RUN apt update && apt install -y \
    opus-tools \
    ffmpeg

COPY . /app

RUN pip3 install poetry
RUN poetry install

CMD [ "poetry", "run", "python3", "main.py" ]
