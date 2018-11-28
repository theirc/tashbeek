import falcon
import json
import requests
import os

from typing import Tuple

from requests.auth import HTTPBasicAuth
from mongoengine import connect, DynamicDocument
from mongoengine.errors import NotUniqueError
import sys
sys.path.append("..")

from models import JobOpening, JobSeeker, Firm, Match
from const import connect_db


COMMCARE_USERNAME = os.environ.get('COMMCARE_USERNAME')
COMMCARE_PASSWORD = os.environ.get('COMMCARE_PASSWORD')
CASES_URL = 'https://www.commcarehq.org/a/billy-excerpt/api/v0.5/case/'

def create_cases(next_params: str, n: int, CaseClass: DynamicDocument) -> Tuple:
    print(f"Getting cases from {CASES_URL}{next_params}")
    resp = requests.get(
        CASES_URL + next_params,
        auth=HTTPBasicAuth(COMMCARE_USERNAME, COMMCARE_PASSWORD)
    )
    cases = json.loads(resp.content)
    for c in cases['objects']:
        params = {**c['properties'], 'case_id': c['case_id']}
        case = CaseClass(**params)
        print(f"Creating case {case.case_id}...")
        try:
            case.save()
        except NotUniqueError as e:
            print(f"{c['case_id']} already exists, skipping...")
        print("saved")
        n += 1

    return (resp, n)

def import_cases(case_type: str, CaseClass: DynamicDocument) -> None:
    limit_offset = '?limit=20&offset=0'
    case_type = f"&type={case_type}&format=json"
    n = 0
    resp, n = create_cases(limit_offset + case_type, n, CaseClass)

    next_params = json.loads(resp.content)['meta']['next']

    while next_params is not None:
        resp, n = create_cases(next_params, n, CaseClass)
        next_params = json.loads(resp.content)['meta']['next']

    print(f"{n} records processed.")


if __name__ == '__main__':
    connect_db()
    print("Creating job openings...")
    import_cases('job-opening', JobOpening)
    print("Creating job seekers...")
    import_cases('job-seeker', JobSeeker)
    print('Creating firms')
    import_cases('firm', Firm)
    print('Creating matches')
    import_cases('match', Match)
