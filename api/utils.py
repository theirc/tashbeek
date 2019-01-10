import pandas as pd
import numpy as np
import json

from sklearn.preprocessing import MultiLabelBinarizer, Imputer
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegressionCV
from sklearn.feature_selection import RFE
from sklearn.feature_selection import chi2

from const import connect_db, categorical_columns, all_columns, scalar_columns
from models import JobSeeker, Firm, JobOpening, Match, JobMatch


def array_vector(col):
    return np.array(str(col))

arrayerize = np.vectorize(array_vector)

def output_coefs(model, X, y):
    coef_dict = {}
    for coef, feat in zip(model.coef_[0], X.columns):
        coef_dict[feat] = coef

    c = {}
    for k, v in coef_dict.items():
        c[k] = [v]


    coef_frame = pd.DataFrame.from_dict(c)
    sorted_frame = coef_frame.columns[coef_frame.ix[coef_frame.last_valid_index()].argsort()]
    coef_frame.to_csv('rfe-coefs.csv')

    odds_ratios = np.exp(coef_frame)
    scores, pvalues = chi2(X, y)

    p_dict = {}
    for pvalue, feat in zip(pvalues, X.columns):
        p_dict[feat] = pvalue

    c = {}
    for k, v in p_dict.items():
        c[k] = [v]


    pval_frame = pd.DataFrame.from_dict(c)
    sorted_frame = pval_frame.columns[pval_frame.ix[pval_frame.last_valid_index()].argsort()]
    pval_frame.to_csv('rfe-pvalues.csv')

    combined = coef_frame.append(pval_frame).append(np.exp(odds_ratios))
    combined.to_csv('rfe-combined.csv')
    X.to_csv('X.csv')
    y.to_csv('y.csv')

def preformat_X(merged):
    formatted = pd.DataFrame()
    dvs = ['hired_yes_no', 'quit', 'fired']
    for col in all_columns:
        if col not in dvs:
            formatted[col] = merged[col]

    for col in all_columns:
        if col not in scalar_columns and col not in dvs:
            formatted = one_hot_encode(formatted, col)

    formatted['case_id'] = merged['JS-case_id']
    to_drop = []
    for col in formatted.columns:
        if col in scalar_columns:
            formatted[col] = formatted[col].apply(try_float)
            mean = formatted[col].mean()
            formatted[col] = formatted[col].replace(['---', ''], mean)
            formatted[col] = formatted[col].fillna(mean)
        elif col != 'case_id':
            formatted[col] = formatted[col].fillna(0)
            formatted[col] = formatted[col].astype(int)
            formatted[col] = formatted[col].replace(['---', ''], 0)

        if col.endswith('---') or col.endswith('nan'):
            to_drop.append(col)

    formatted = formatted.drop(columns=to_drop)
    return formatted

def one_hot_encode(df, column, labels_column=None, whitelist=[]):
    # This is gross but since strings are iterable, we have to wrap them in a list
    # in order for the binarizer to parse the labels as strings and not chars
    labels = arrayerize(pd.DataFrame(df[column]))
    terms = arrayerize(pd.DataFrame(list(set(df[column]))))

    mlb = MultiLabelBinarizer()
    mlb.fit(terms)
    mlb.transform(labels)
    columns = [ f'{column}-{classname}' for classname in  mlb.classes_]

    encoded = pd.DataFrame(mlb.transform(labels), columns=columns, index=df[column].index)

    df.drop(column, axis=1, inplace=True)
    return df.join(encoded)

def try_float(v):
    try:
        return float(v)
    except Exception as e:
        return np.nan

def get_x_y(job_seekers, firms, matches, jobs):
    matches['parent_case_id'] = matches['MATCH-parent_case_id']
    job_seekers['parent_case_id'] = job_seekers['JS-case_id']
    merged = pd.merge(job_seekers, matches, on='parent_case_id')
    merged = pd.merge(merged, jobs, on='job_id')

    # Drop irrelevant columns that will throw off our predictions
    merged = merged.drop(["MATCH-hh_income", "MATCH-interest_applying", "MATCH-num_children", "MATCH-personal_income"], axis=1)

    merged['hired_yes_no'] = merged['hired_yes_no'].fillna(0)
    merged['hired_yes_no'] = merged['hired_yes_no'].replace(['---'], 0)

    merged['quit'] = merged['quit'].fillna(0)
    merged['quit'] = merged['quit'].replace(['---'], 0)
    merged['quit'] = merged['quit'].replace(['no'], 0)
    merged['quit'] = merged['quit'].replace(['yes'], 1)

    merged['fired'] = merged['fired'].fillna(0)
    merged['fired'] = merged['fired'].replace(['---'], 0)
    merged['fired'] = merged['fired'].replace(['no'], 0)
    merged['fired'] = merged['fired'].replace(['yes'], 1)

    merged['hired_yes_no'] = merged['hired_yes_no'].astype(bool)
    merged['quit'] = merged['quit'].astype(bool)
    merged['fired'] = merged['fired'].astype(bool)
    outcomes = pd.DataFrame()
    outcomes['retained'] = merged['hired_yes_no'] & ~(merged['quit'] | merged['fired'])
    outcomes['hired'] = merged['hired_yes_no']
    y = pd.DataFrame()
    o = []
    for index, row in outcomes.iterrows():
        if row['hired'] and row['retained']:
            o.append(2)
        elif not row['hired'] and not row['retained']:
            o.append(0)
        elif row['hired'] and not row['retained']:
            o.append(1)
    y['outcomes'] = outcomes['hired']
    y = y.astype(int)

    X = preformat_X(merged)
    return X, y

def train_model(X, y):
    model = LogisticRegressionCV(max_iter=1000, solver='liblinear', penalty='l1', cv=3)
    selector = RFE(model, 20, step=4)
    selector.fit(X, y)
    cols = []
    XX = pd.DataFrame()
    for i, v in enumerate(selector.support_):
        if v:
            cols.append(X.columns[i])
    for c in cols:
        XX[c] = X[c]

    model.fit(XX, y)
    output_coefs(model, XX, y)
    return model, XX
def filter_job_seekers(job_seekers, firm, job):
    print(job_seekers.shape)
    print('city: ' + firm['JOB-fcity'].values[0])
    #city
    job_seekers = job_seekers[job_seekers['JS-city'] == firm['JOB-fcity'].values[0]]

    print(job_seekers.shape)
    print('syrian considered: ' + job['JOB-syrian_considered'])
    # nationality
    if job['JOB-syrian_considered'] == 'no':
        job_seekers = job_seekers[job_seekers['JS-nationality'] != 'syrian']

    print(job_seekers.shape)
    print('male/female required: ' + job['JOB-male_required'] + job['JOB-female_requied'])
    # genders
    if job['JOB-male_required'] == 'yes' and  job['JOB-female_requied'] == 'no':
        job_seekers = job_seekers[job_seekers['JS-gender'] == 'male']

    # TODO: mispelling in required here
    if job['JOB-female_requied'] == 'yes' and job['JOB-male_required'] == 'no':
        job_seekers = job_seekers[job_seekers['JS-gender'] == 'female']

    print(job_seekers.shape)
    print(f"age accepted: {job['JOB-age_accepted']}")

    # age
    job_seekers['JS-age'] = job_seekers['JS-age'].apply(try_float)
    if not type(job['JOB-age_accepted']) and np.isnan(job['JOB-age_accepted']):
        ranges = job['JOB-age_accepted'].split(' ')
    else:
        ranges = '---'
    if '---' not in ranges:
        for age_range in ranges:
            print(age_range)
            lower, higher = age_range.split('_')
            job_seekers = job_seekers[job_seekers['JS-age'] > int(lower)]
            job_seekers = job_seekers[job_seekers['JS-age'] < int(higher)]

    print(job_seekers.shape)
    print(f"sez: {firm['JOB-sez_firm']}")
    # qiz
    if firm['JOB-sez_firm'].values[0] == 'yes':
        # Include NA answers as well
        job_seekers = job_seekers[job_seekers['JS-will_work_qiz'] != 0]

    # physical work
    print(job_seekers.shape)
    print('physical: ' + job['JOB-physical_work_abilities_required'])
    if job['JOB-physical_work_abilities_required'] == 'yes':
        # Include NA answers as well
        job_seekers = job_seekers[job_seekers['JS-will_do_physical_work'] != 0]

    print(job_seekers.shape)
    print('night shifts: ' + job['JOB-night_shifts_required'])
    # night shift
    if job['JOB-night_shifts_required'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-will_work_night_shift'] != 0]

    print('dorm: ' + job['JOB-dorm_covered'])
    print(job_seekers.shape)
    # dorm
    if job['JOB-dorm_covered'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-will_live_in_dorm'] != 0]

    print(job_seekers.shape)
    print(f"unpaid training: {job['JOB-unpaid_training_required']}")
    # unpaid training
    if job['JOB-unpaid_training_required'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-will_train_unpaid'] == 1]

    print(job_seekers.shape)
    print(f"education: {job['JOB-education_required']}")

    # education
    replace = {
        'college_technical': 'college',
        'diploma_nontech': 'diploma',
        'no_school': 'none'
    }
    for k, v in replace.items():
        job['JOB-education_required'] = job['JOB-education_required'].replace(k, v)

    educations = ['doctorate', 'masters', 'bachelors', 'diploma', 'college', 'secondary', 'intermediate', 'primary', 'none', np.nan]

    i = educations.index(job['JOB-education_required'])
    educations[:i + 1]
    job_seekers = job_seekers[job_seekers['JS-highest_edu_level'].isin(educations[:i + 1])]

    print(job_seekers.shape)
    print(f"literacy required: {job['JOB-literacy_required']}")
    # literacy
    if job['JOB-literacy_required'] == 'yes':
        job_seekers = job_seekers[job_seekers['JS-is_literate'] != 0]

    job_seekers = job_seekers.replace(['---'], 0)
    if not np.isnan(float(job['JOB-years_experience_required'])):
        job_seekers['JS-years_exp'] = job_seekers['JS-years_exp']
        job_seekers = job_seekers[job_seekers['JS-years_exp'].apply(try_float) > float(job['JOB-years_experience_required'])]

    print(job_seekers.shape)
    return job_seekers

def get_match_scores(job_id):
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

    print('got db items')
    ignore = ['number', 'caseid', 'parent_caseid', 'job_id', 'hired_yes_no', 'quit', 'fired']
    # Do some column formatting to help with analysis
    job_seekers.columns = ['JS-' + c if c not in ignore else c for c in job_seekers.columns]
    firms.columns = ['JOB-' + c if c not in ignore else c for c in firms.columns]
    jobs.columns = ['JOB-' + c if c not in ignore else c for c in jobs.columns]
    matches.columns = ['MATCH-' + c if c not in ignore else c for c in matches.columns]

    # Select job ID and do some basic formatting to join everything together
    job = jobs[jobs['job_id'] == job_id].squeeze()
    job_seekers = job_seekers[job_seekers['JS-testing'] != 'yes']
    firm = firms[firms['JOB-case_id'] == job['JOB-parent_case_id']]

    print('training model')
    # Train our model
    X, y = get_x_y(job_seekers, firms, matches, jobs)
    X.drop(['case_id'], axis=1, inplace=True)
    model, X = train_model(X, y)

    # Run the actual filter
    merged = filter_job_seekers(job_seekers, firm, job)

    # all post-filter job seekers 1 hot encoded for our test set
    for k in job.keys():
        merged[k] = job[k]
    for k in firm.keys():
        merged[k] = firm[k]

    merged = preformat_X(merged)

    # Limit to feature selected columns
    test_X = pd.DataFrame()
    for col in X.columns:
        try:
            test_X[col] = merged[col]
        except KeyError as e:
            test_X[col] = 0

    # Run the actual prediction here
    probs = model.predict_proba(test_X)
    output = pd.DataFrame()
    output['probs'] = probs.T[1]
    output['case_id'] = merged['case_id'].values
    output = output.round({'probs': 5})
    test_X.to_csv('test_X.csv')
    output.to_csv('output.csv')
    return output

def create_match_object(job_id):
    print('create match object')
    match_scores = get_match_scores(job_id)
    scores_list = json.loads(match_scores.T.to_json()).values()
    try:
        connect_db()
        match = JobMatch.objects.get(job_id=job_id)
        match.update(scores=list(scores_list), status='complete')
        print('match updated')
    except Exception as e:
        print("error: ", e)

# This is just used for testing
if __name__ == '__main__':
    connect_db()
    job_id = 'XCHJQ3'
    scores = create_match_object(job_id)
    print('scores')
