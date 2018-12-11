import pandas as pd
import numpy as np

from const import connect_db, categorical_columns, all_columns, scalar_columns
from models import JobSeeker, Firm, JobOpening, Match


JOB_ID = 40

def try_float(v):
    try:
        return float(v)
    except Exception as e:
        return np.nan

def get_match_scores():
    job_seeker_models = JobSeeker.objects.all()
    job_opening_models = JobOpening.objects.all()
    firm_models = Firm.objects.all()
    match_models = Match.objects.all()

    job_seeker_json = [js.to_mongo() for js in job_seeker_models]
    job_opening_json = [jo.to_mongo() for jo in job_opening_models]
    firm_json = [firm.to_mongo() for firm in firm_models]
    match_json = [match.to_mongo() for match in match_models]

    job_seekers = pd.DataFrame(job_seeker_json)
    jobs = pd.DataFrame(job_opening_json)
    firms = pd.DataFrame(firm_json)
    matches = pd.DataFrame(match_json)

    ignore = ['number', 'caseid', 'parent_caseid', 'job_id', 'hired_yes_no', 'quit', 'fired']

    job_seekers.columns = ['JS-' + c if c not in ignore else c for c in job_seekers.columns]
    firms.columns = ['JOB-' + c if c not in ignore else c for c in firms.columns]
    jobs.columns = ['JOB-' + c if c not in ignore else c for c in jobs.columns]
    matches.columns = ['MATCH-' + c if c not in ignore else c for c in matches.columns]

    job = jobs.loc[JOB_ID]
    job_seekers = job_seekers[job_seekers['JS-testing'] != 'yes']
    firm = firms[firms['JOB-case_id'] == job['JOB-parent_case_id']]

    print('city: ' + firm['JOB-fcity'].values[0])
    print(job_seekers.shape)
    #city
    job_seekers = job_seekers[job_seekers['JS-city'] == firm['JOB-fcity'].values[0]]

    print('syrian considered: ' + job['JOB-syrian_considered'])
    print(job_seekers.shape)
    # nationality
    if job['JOB-syrian_considered'] == 'no':
        job_seekers = job_seekers[job_seekers['JS-nationality'] != 'syrian']

    print('male/female required: ' + job['JOB-male_required'] + job['JOB-female_requied'])
    print(job_seekers.shape)
    # genders
    if job['JOB-male_required'] == 'yes' and  job['JOB-female_requied'] == 'no':
        job_seekers = job_seekers[job_seekers['JS-gender'] == 'male']

    # TODO: mispelling in required here
    if job['JOB-female_requied'] == 'yes' and job['JOB-male_required'] == 'no':
        job_seekers = job_seekers[job_seekers['JS-gender'] == 'female']

    print(f"age accepted: {job['JOB-age_accepted']}")
    print(job_seekers.shape)

    # age
    job_seekers['JS-age'] = job_seekers['JS-age'].astype(float)
    ranges = job['JOB-age_accepted'].split(' ') if not np.isnan(job['JOB-age_accepted']) else ['---']
    if '---' not in ranges:
        for age_range in ranges:
            print(age_range)
            lower, higher = age_range.split('_')
            job_seekers = job_seekers[job_seekers['JS-age'] > int(lower)]
            job_seekers = job_seekers[job_seekers['JS-age'] < int(higher)]

    print(f"sez: {firm['JOB-sez_firm']}")
    print(job_seekers.shape)
    # qiz
    if firm['JOB-sez_firm'].values[0] == 'yes':
        # Include NA answers as well
        job_seekers = job_seekers[job_seekers['JS-will_work_qiz'] != 0]

    # physical work
    print('physical: ' + job['JOB-physical_work_abilities_required'])
    print(job_seekers.shape)
    if job['JOB-physical_work_abilities_required'] == 'yes':
        # Include NA answers as well
        job_seekers = job_seekers[job_seekers['JS-will_do_physical_work'] != 0]

    print('night shifts: ' + job['JOB-night_shifts_required'])
    print(job_seekers.shape)
    # night shift
    if job['JOB-night_shifts_required'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-will_work_night_shift'] != 0]

    print('dorm: ' + job['JOB-dorm_covered'])
    print(job_seekers.shape)
    # dorm
    if job['JOB-dorm_covered'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-will_live_in_dorm'] != 0]

    print(f"unpaid training: {job['JOB-unpaid_training_required']}")
    print(job_seekers.shape)
    # unpaid training
    if job['JOB-unpaid_training_required'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-will_train_unpaid'] == 1]

    print(f"education: {job['JOB-education_required']}")
    print(job_seekers.shape)

    # education
    replace = {
        'college_technical': 'college',
        'diploma_nontech': 'diploma'
    }
    educations = ['none', 'primary', 'secondary', 'college', 'diploma', 'bachelors', 'masters', 'doctorate', np.nan]

    i = educations.index(job['JOB-education_required'])
    educations[:i + 1]
    job_seekers = job_seekers[job_seekers['JS-highest_edu_level'].isin(educations[:i + 1])]

    print(f"literacy required: {job['JOB-literacy_required']}")
    print(job_seekers.shape)
    # literacy
    if job['JOB-literacy_required'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-is_literate'] != 0]

    job_seekers = job_seekers.replace(['---'], 0)
    if not np.isnan(float(job['JOB-years_experience_required'])):
        job_seekers['JS-years_exp'] = job_seekers['JS-years_exp'].apply(try_float)
        job_seekers = job_seekers[job_seekers['JS-years_exp'].astype(float) > float(job['JOB-years_experience_required'])]

    print(job_seekers.shape)


def train_model(job_seekers, firms, matches, jobs):
    pass

if __name__ == '__main__':
    connect_db()
    get_match_scores()
