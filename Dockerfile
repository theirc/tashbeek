# Use an official Python runtime as a parent image
FROM python:3

COPY ./api/ /app
COPY ./requirements.txt /app/

RUN pip install -r /app/requirements.txt
WORKDIR "/app/"

CMD gunicorn --workers=5 -b '0.0.0.0:8000' -k gevent app
