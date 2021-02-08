FROM python:3.7-slim-buster

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY . /src/xapp

WORKDIR /src/xapp

CMD [ "python3", "xapp_main.py" ]

