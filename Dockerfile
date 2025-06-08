FROM python:3.12-rc-slim-buster

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY . /app


RUN pip install -r requirements.txt


EXPOSE 5000


CMD [ "python", "app.py" ]