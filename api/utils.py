import pandas as pd
import numpy as np
import json

from sklearn.preprocessing import MultiLabelBinarizer, Imputer
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegressionCV
from sklearn.feature_selection import RFE
from sklearn.feature_selection import chi2

from const import connect_db, disconnect_db, categorical_columns, all_columns, scalar_columns
from models import JobSeeker, Firm, JobOpening, Match, JobMatch


"""
Utility function for formatting a column into an array vector based on spaces
in the cell value

@param {Series} col - Any pandas series object

@return {np.array} - numpy vector of the column now split
"""
def array_vector(col):
    # Split all values in the cell on space
    return np.array(str(col).split(' '), dtype=object)[0]


arrayerize = np.vectorize(array_vector)


"""
Helper function for outputting csv with information on our model

Specifically the files output are below:
    rfe-coefs.csv -     This is the correlation coefficients for each independent 
                        variable in the model.
    rfe-pvalues.csv -   This is the p-values for each independent variable in
                        the model.
    rfe-combined.csv -  This is a nicely formatted version of the two above 
                        files.
    X.csv -             This is the independent variables.
    Y.csv -             This is the dependent variables.

@param {LogisticRegressionCV} model - This is the model we want the information
                                      from
@param {DataFrame} X - This is the DataFrame containing the independent vars
                       to train the model on.
@param {DataFrame} y - This contains the dependent (outcome) variables to train
                       the model on.

@return void
"""
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



"""
Prep our X training set to be used in our model. Normalize and fill in any
blank data. Remove DVs from training set.

@param {DataFrame} merged - This is the X training data set

@return {DataFrame} formatted - The X training data set now formatted to be fed
                                in to the model.
"""
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

        if col.endswith('---') or col.endswith('nan') or col.endswith('-'):
            to_drop.append(col)

    formatted = formatted.drop(columns=to_drop)
    return formatted

"""
Helper function for one hot encoding a dataframe column

@param {DataFrame} df - The frame to one-hot encode
@param {string} column - The name of the column to encode

@return {DataFrame} df - The dataframe with the column now encoded
"""
def one_hot_encode(df, column):
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

"""
Cast float or NaN on exception

@param {any} v - Any variable

@return {float} - either float(v) or NaN if it can't be casted.
"""
def try_float(v):
    try:
        return float(v)
    except Exception as e:
        return np.nan

"""
Given database of job_seekers, firms, matches, and job openings, return
the relevant X and y dataframes


@param {DataFrame} job_seekers - DataFrame representing all job seekers &
                                 properties pulled from CommCare.
@param {DataFrame} firms - DataFrame representing the firms from CommCare.
@param {DataFrame} matches - DataFrame representing matches from CommCare.
@param {DataFrame} job - Dataframe representing the jobs from CommCare.

@param {tuple(X, y)} X, y - Both the X and y portion of the training data
                            formatted to be used correctly by our model.
"""
def get_x_y(job_seekers, firms, matches, jobs):
    job_seekers.drop(['quit', 'hired_yes_no', 'fired'], axis=1, inplace=True)
    matches['parent_case_id'] = matches['MATCH-parent_case_id']
    job_seekers['parent_case_id'] = job_seekers['JS-case_id']
    merged = pd.merge(job_seekers, matches, on='parent_case_id')
    merged = pd.merge(merged, jobs, on='job_id')

    # Drop irrelevant columns that will throw off our predictions
    merged = merged.drop(
        ["MATCH-hh_income", "MATCH-interest_applying", "MATCH-num_children",
         "MATCH-personal_income", "JS-city", "JOB-num_vacancies"],
        axis=1
    )

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
    y = pd.DataFrame()
    outcomes = pd.DataFrame()
    # No longer using retained variable in the algorithm
    # outcomes['retained'] = merged['hired_yes_no'] & ~(merged['quit'] | merged['fired'])
    outcomes['hired'] = merged['hired_yes_no']
    # o = []
    # for index, row in outcomes.iterrows():
    #     if row['hired'] and row['retained']:
    #         o.append(2)
    #     elif not row['hired'] and not row['retained']:
    #         o.append(0)
    #     elif row['hired'] and not row['retained']:
    #         o.append(1)
    y['outcomes'] = outcomes['hired']
    y = y.astype(int)

    X = preformat_X(merged)
    return X, y

"""
Train our model using a Logistic Regression with Cross Validation and Lasso
method.

@param {DataFrame} X - This is the DataFrame containing the independent vars
                       to train the model on.
@param {DataFrame} y - This contains the dependent (outcome) variables to train
                       the model on.

@return {tuple(LogisticRegressionCV, DataFrame)} (model, X) - A tuple
        containing a copy of the X training set, as well as the newly trained
        model
"""
def train_model(X, y):
    X.to_csv('./X.csv')
    model = LogisticRegressionCV(max_iter=1000, solver='liblinear', penalty='l1', cv=3)

    print("fitting model...")
    model.fit(X, y)
    # output_coefs(model, X, y)
    return model, X
"""
Run our criteria filters to remove unqualified candidates.

@param {DataFrame} job_seekers - DataFrame representing all job seekers &
                                 properties pulled from CommCare.
@param {DataFrame} firm - DataFrame representing the firm which is being matched
                          in to.
@param {DataFrame} job - Dataframe representing the job which is being matched
                         in to.

@return {DataFrame} job_seekers - This is the newly filtered job_seekers dataframe
"""
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
    if not np.isnan(try_float(job['JOB-years_experience_required'])):
        job_seekers['JS-years_exp'] = job_seekers['JS-years_exp']
        job_seekers = job_seekers[job_seekers['JS-years_exp'].apply(try_float) > try_float(job['JOB-years_experience_required'])]

    print(job_seekers.shape)
    return job_seekers

"""
Helper function to get job_seeker ranks for a given job opening

This is the entrypoint into the "matching algorithm"

@param {int} job_id - This is the UID of the job to perform matching on

@return {DataFrame} output - Dataframe containing case_id's and corresponding
                             match scores
"""
def get_match_scores(job_id):
    job_seeker_models = JobSeeker.objects.all()
    job_opening_models = JobOpening.objects.all()
    firm_models = Firm.objects.all()
    match_models = Match.objects.all()
    print('got db items')

    job_seeker_json = [js.to_mongo() for js in job_seeker_models]
    job_opening_json = [jo.to_mongo() for jo in job_opening_models]
    firm_json = [firm.to_mongo() for firm in firm_models]
    match_json = [match.to_mongo() for match in match_models]

    job_seekers = pd.DataFrame(job_seeker_json)
    jobs = pd.DataFrame(job_opening_json)
    firms = pd.DataFrame(firm_json)
    matches = pd.DataFrame(match_json)

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

    # Train our model
    X, y = get_x_y(job_seekers, firms, matches, jobs)

    X.drop(['case_id'], axis=1, inplace=True)
    for col in X.columns:
        if not all(ord(c) < 128 for c in col):
            X.drop([col], axis=1, inplace=True)

    print('training model')
    model, X = train_model(X, y)

    # Run the actual filter
    merged = filter_job_seekers(job_seekers, firm, job)

    # Don't bother running the algorithm if no one makes it through
    if len(merged.index) == 0:
        return pd.DataFrame(columns=['probs', 'case_id'])

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
    # The following lines is for debugging and analysis of output and test data.
    # test_X.to_csv('test_X.csv')
    # output.to_csv('output.csv')
    return output

"""
Create match database object and get scores

@param {int} job_id - This is the UID of the job to perform matching on

@return void
"""
def create_match_object(job_id):
    print('create match object')
    match = JobMatch(job_id=job_id, status='processing')
    match.save()
    match_scores = get_match_scores(job_id)
    scores_list = json.loads(match_scores.T.to_json()).values()
    try:
        connect_db()
        match = JobMatch.objects.get(job_id=job_id)
        match.update(scores=list(scores_list), status='complete')
        print('match updated')
    except Exception as e:
        print("error: ", e)
    finally:
        disconnect_db()

# This is just used for testing
if __name__ == '__main__':
    connect_db()
    job_id = 'TPHLBC'
    scores = create_match_object(job_id)
    disconnect_db()
    print('scores')
