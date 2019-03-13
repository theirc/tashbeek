import pandas as pd
import itertools

from const import connect_db
from models import JobSeeker

def has_intervention(j, i):
    return 1 if j['actual_intervention_received'] == i else 0

def set_strata(j, stratum):
    test = [j['nationality'], j['gender'], j['above_secondary_edu'], j['ever_employed']]
    return stratum[(stratum['nationality'] == test[0]) &
            (stratum['gender'] == test[1]) &
            (stratum['above_secondary_edu'] == test[2]) &
            (stratum['ever_employed'] == test[3])].index[0]

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

    new['outcome'] = job_seekers['employed_6_week']
    new['outcome'].replace(['0'], 'FALSE', inplace=True)
    new['outcome'].replace(['1'], 'TRUE', inplace=True)
    return new

def run_thompson() -> None:
    js_models = JobSeeker.objects(year2="1")
    job_seekers = pd.DataFrame([js.to_mongo() for js in js_models])
    job_seekers = job_seekers[job_seekers['employed_6_week'].isin(['0', '1'])]
    thompson_input = format_input(job_seekers)
    return thompson_input


if __name__ == '__main__':
    connect_db()
    run_thompson()
