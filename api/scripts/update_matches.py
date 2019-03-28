from datetime import datetime

from models import JobOpening, JobMatch, Cron
from const import connect_db, disconnect_db
from utils import create_match_object

def run_matches():
    print("Calculating optimal matches...")
    open_jobs = JobOpening.objects(closed=False)
    for job in open_jobs:
        if not JobMatch.objects(job_id=job.job_id):
            print(f'Calculating match for {job.job_id}')
            create_match_object(job.job_id)
        else:
            print(f'Skipping {job.job_id} already exists')


if __name__ == '__main__':
    cron = Cron(date=datetime.now(), status='processing', cron_type='update_matches')
    connect_db()
    try:
        cron.save()
        run_matches()
        cron.status = 'finished'
        cron.save()
    except Exception as e:
        cron.status = 'error'
        cron.error = e.message
        cron.save()
    finally:
        disconnect_db()
