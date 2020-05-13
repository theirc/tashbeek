import dropbox
import itertools
import pandas as pd
import subprocess
from datetime import datetime
import os
from const import connect_db, disconnect_db, DROPBOX_KEY
from models import JobSeeker, ThompsonProbability, Cron


def get_last_treatment_probabilities_file_in_dropbox():
    dbx = dropbox.Dropbox(DROPBOX_KEY)
    all_files = dbx.files_list_folder('').entries
    all_files = list(filter(lambda file: 'treatmentprobabilities.csv' in file.name, all_files))
    last_file = all_files[-1].name
    print(last_file)
    return all_files[-1]


def has_intervention(j, i):
    return 1 if j['actual_intervention_received'] == i else 0

def set_strata(j, stratum):
    test = [j['nationality'], j['gender'], j['above_secondary_edu'], j['ever_employed']]
    return stratum[(stratum['nationality'] == test[0]) &
                   (stratum['gender'] == test[1]) &
                   (stratum['above_secondary_edu'] == test[2]) &
                   (stratum['ever_employed'] == test[3])].index[0] + 1

def format_input(job_seekers: pd.DataFrame) -> pd.DataFrame:
    nationality = ['syrian', 'jordanian']
    gender = ['male', 'female']
    secondary = ['0', '1']
    work = ['0', '1']
    cols = ['nationality', 'gender', 'above_secondary_edu', 'ever_employed']
    lists = [nationality, gender, secondary, work]

    # Build dataframe of stratum ids
    stratum = pd.DataFrame(list(itertools.product(*lists)), columns=cols)

    new = pd.DataFrame()
    new['covar1'] = job_seekers.apply(set_strata, args=(stratum,), axis=1)
    new['treatment1'] = job_seekers.apply(has_intervention, args=('cash',),
                                          axis=1)
    new['treatment2'] = job_seekers.apply(has_intervention,
                                          args=('information',), axis=1)
    new['treatment3'] = job_seekers.apply(has_intervention,
                                          args=('psychological',), axis=1)
    new['treatment4'] = job_seekers.apply(has_intervention,
                                          args=('control',), axis=1)

    new['outcome'] = job_seekers['employed_6_week']
    new['outcome'].replace(['0'], 'FALSE', inplace=True)
    new['outcome'].replace(['1'], 'TRUE', inplace=True)
    new['intake_interview_date'] = job_seekers['intake_interview_date']
    new['case_id'] = job_seekers['case_id']

    # Upload prior data to dropbox
    dbx = dropbox.Dropbox(DROPBOX_KEY)
    now = datetime.now().strftime('%Y-%m-%d')
    filename = f'{now}_priordata.csv'
    filepath = f'/app/scripts/ThompsonHierarchicalApp/{filename}'
    new.to_csv(filepath)
    try:
        with open(filepath, 'rb') as f_in:
            dbx.files_upload(f_in.read(), f'/{filename}')
    except:
        pass

    subprocess.run(['rm', filepath])

    new.drop(['intake_interview_date'], inplace=True, axis=1)
    return new

def exec_r_script() -> str:
    p = subprocess.Popen(
        ['Rscript', '/app/scripts/ThompsonHierarchicalApp/command_line_app.R',
         '/app/scripts/ThompsonHierarchicalApp/priordata_test_missings.csv'],
        cwd='/app/scripts/ThompsonHierarchicalApp/',
    )
    stdout, stderr = p.communicate()
    p.wait()

    print(stdout, stderr)
    probs_text = ''
    now = datetime.now().strftime('%Y-%m-%d')
    probs_file_name = f'/app/scripts/ThompsonHierarchicalApp/{now}_treatmentprobabilities.csv'
    try:
        with open(probs_file_name) as probs:
            probs_text = ''.join(probs.readlines())
    except:
        last_file = get_last_treatment_probabilities_file_in_dropbox()
        last_file_path = last_file.path_display
        dbx = dropbox.Dropbox(DROPBOX_KEY)
        dbx.files_download_to_file(f'scripts/ThompsonHierarchicalApp/{now}_treatmentprobabilities.csv', last_file_path)
        with open(probs_file_name) as probs:
            probs_text = ''.join(probs.readlines())
    return probs_text


def run_thompson() -> None:
    print('hello world')
    js_models = JobSeeker.objects(year2="1")
    job_seekers = pd.DataFrame([js.to_mongo() for js in js_models])
    job_seekers = job_seekers[job_seekers['employed_6_week'].isin(['0', '1'])]
    job_seekers = job_seekers[job_seekers['actual_intervention_received'].isin(
        ['control', 'information', 'psychological', 'cash']
    )]
    thompson_input = format_input(job_seekers)
    now = datetime.now().strftime('%Y-%m-%d')
    probs_file_name = f'/app/scripts/ThompsonHierarchicalApp/{now}_treatmentprobabilities.csv'
    input_file_name = '/app/scripts/ThompsonHierarchicalApp/priordata_test_missings.csv'
    thompson_input.to_csv(
        input_file_name,
        index=False
    )

    # Save to database
    print(thompson_input)
    probs_text = exec_r_script()
    print(probs_text)

    prob = ThompsonProbability(date=datetime.now(), probs=probs_text)
    print(probs_text)
    prob.save()

    # Upload probabilities to dropbox
    dbx = dropbox.Dropbox(DROPBOX_KEY)
    now = datetime.now().strftime('%Y-%m-%d')
    filename = f'{now}_treatmentprobabilities.csv'
    filepath = f'/app/scripts/ThompsonHierarchicalApp/{filename}'
    with open(filepath, 'rb') as f_in:
        dbx.files_upload(f_in.read(), f'/{filename}')

    # Clean up local files
    subprocess.run(['rm', probs_file_name])
    subprocess.run(['rm', input_file_name])

if __name__ == '__main__':
    cron = Cron(date=datetime.now(), status='processing', cron_type='run_thompson')
    connect_db()
    try:
        cron.save()
        run_thompson()
        cron.status = 'finished'
        cron.save()
    except Exception as e:
        print(str(e))
        cron.status = 'error'
        cron.error = str(e)
        cron.save()
    finally:
        disconnect_db()
