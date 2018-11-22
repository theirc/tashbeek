# Use an official Python runtime as a parent image
FROM python:3

COPY ./src/ /app
COPY ./requirements.txt /app/

RUN pip install -r /app/requirements.txt
WORKDIR "/app/"

# CMD python3 -m http.server
CMD gunicorn --reload -b '0.0.0.0:8000' sheriff.app
