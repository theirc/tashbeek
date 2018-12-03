# Use an official Python runtime as a parent image
FROM python:3

#COPY ./api/ /app
COPY ./requirements.txt /app/

RUN pip install -r /app/requirements.txt
RUN pip install requests mongoengine gunicorn
WORKDIR "/app/"

# CMD python3 -m http.server
CMD gunicorn --reload -b '0.0.0.0:8000' app
