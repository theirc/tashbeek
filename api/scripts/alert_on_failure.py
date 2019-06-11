import dropbox
import itertools
import pandas as pd
import subprocess
from datetime import datetime
import os
from const import connect_db, disconnect_db, DROPBOX_KEY
from models import JobSeeker, ThompsonProbability, Cron
import smtplib


def get_last_treatment_probabilities_file_in_dropbox():
    dbx = dropbox.Dropbox(DROPBOX_KEY)
    all_files = dbx.files_list_folder('').entries
    all_files = list(filter(lambda file: 'treatmentprobabilities.csv' in file.name, all_files))
    return all_files[-1]


def failure():
    last_file = get_last_treatment_probabilities_file_in_dropbox()
    now = datetime.now().strftime('%Y-%m-%d')
    return last_file.name != f'{now}_treatmentprobabilities.csv'


def send_mail():
    hostname = os.environ.get('EMAIL_HOST')
    port = int(os.environ.get('EMAIL_PORT'))
    mail_user = os.environ.get('EMAIL_USERNAME')
    mail_password = os.environ.get('EMAIL_PASSWORD')
    mail_from = os.environ.get('EMAIL_FROM')
    mail_from = 'IRC Souktel <%s>' % mail_from
    mail_to = os.environ.get('EMAIL_TO')

    now = datetime.now().strftime('%Y-%m-%d')
    subject = 'Error with thompson file'
    body = f'An error occurred while running Thompson application for {now}\n\r' \
           f'Can\'t find the file {now}_treatmentprobabilities.csv in the Dropbox folder\n\r' \
           f'https://www.dropbox.com/sh/qwh4b6e7vvqes6x/AADd3Pd6ZEPhUMeVOd50lWhva/IRC-Thompson'

    mail_text = """\
    Subject: %s
    From: %s
    To: %s
    
    %s
    """ % (subject, mail_from, mail_to, body)

    try:
        server = smtplib.SMTP(hostname, port)
        # server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(mail_user, mail_password)
        server.sendmail(mail_from, mail_to.split(","), mail_text)
        server.quit()

        print('Email sent')

    except Exception as e:
        print('something went wrong...')
        print(e)


if __name__ == '__main__':
    if failure():
        send_mail()
