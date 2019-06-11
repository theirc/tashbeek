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
    print('Sending Email ..')

    now = datetime.now().strftime('%Y-%m-%d')

    msg = f'''\\
             ... From: {os.environ.get('EMAIL_FORM')}
             ... Subject: Error with thompson file'...
             ...
             ... Error in run thompson script [Can\'t find {now}_treatmentprobabilities.csv file'''
    server = smtplib.SMTP_SSL(os.environ.get('EMAIL_HOST'), int(os.environ.get('EMAIL_PORT')))

    try:
        server.ehlo()
        server.login(os.environ.get('EMAIL_USERNAME'), os.environ.get('EMAIL_PASSWORD'))
        server.sendmail(
            os.environ.get('EMAIL_FORM'),
            os.environ.get('EMAIL_TO'),
            msg)
        server.close()

    except:
        print('Something went wrong...')


if __name__ == '__main__':
    if failure():
        send_mail()
