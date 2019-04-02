import pandas as pd
import itertools
import subprocess
from datetime import datetime

from const import connect_db, disconnect_db
from models import JobSeeker, ThompsonProbability, Cron

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
    # new.to_csv('./outcomes.csv')
    return new

def exec_r_script() -> str:
    p = subprocess.Popen(
        ['Rscript', '/app/scripts/ThompsonHierarchicalApp/command_line_app.R',
        '/app/scripts/ThompsonHierarchicalApp/priordata_test_missings.csv'],
        cwd='/app/scripts/ThompsonHierarchicalApp/',
    )
    stdout,stderr = p.communicate()
    p.wait()

    print(stdout, stderr)
    probs_text = ''
    now = datetime.now().strftime('%Y-%m-%d')
    probs_file_name = f'/app/scripts/ThompsonHierarchicalApp/{now}_treatmentprobabilities.csv'
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
    print(thompson_input)
    probs_text = exec_r_script()
    print(probs_file_name)
    with open(probs_file_name) as probs:
        probs_text = ''.join(probs.readlines())
    prob = ThompsonProbability(date=datetime.now(), probs=probs_text)
    print(probs_text)
    prob.save()
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
