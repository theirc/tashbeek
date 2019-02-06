# Use an official Python runtime as a parent image
FROM python:3

RUN pip install -U pip

COPY ./requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY ./api/ /app
WORKDIR "/app/"

# Install tools needed for cron and supervisor
RUN apt-get update
RUN apt-get install -y cron supervisor openssh-server
RUN mkdir -p /var/log/supervisor
# Below is the file for daemons we will be starting in this container
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy cronjobs into docker container and run it
COPY crontab /etc/cron.hourly/crontab
RUN chmod 0644 /etc/cron.hourly/crontab
RUN crontab /etc/cron.hourly/crontab

EXPOSE 2222 80

COPY startup.sh /startup.sh
RUN chmod +x /startup.sh
CMD ["/startup.sh"]
