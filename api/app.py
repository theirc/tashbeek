import falcon
import json
import requests
import os

from requests.auth import HTTPBasicAuth
from mongoengine import connect

from models import JobOpening, JobSeeker, Firm, Match, User
from const import connect_db


COMMCARE_USERNAME = os.environ.get('COMMCARE_USERNAME')
COMMCARE_PASSWORD = os.environ.get('COMMCARE_PASSWORD')
CASES_URL = 'https://www.commcarehq.org/a/billy-excerpt/api/v0.5/case/'

connect_db()

class ScoresResource(object):
    def on_get(self, req, resp):
        url = 'https://www.dropbox.com/s/p0jdw71vwu1quru/scores.csv'
        r = requests.get(url)
        print(r.body)
        resp.body = '{"hello": "world"}'

class JobMatchResource(object):
    def on_get(self, req, resp):
        resp.body = '{"hello": "world"}'

class JobOpeningResource(object):
    def on_get(self, req, resp):
        openings = JobOpening.objects.all()
        resp.body = openings.to_json()

class JobSeekerResource(object):
    def on_get(self, req, resp):
        job_seekers = JobSeeker.objects.all()
        resp.body = job_seekers.to_json()

class FirmResource(object):
    def on_get(self, req, resp):
        firms = Firm.objects.all()
        resp.body = firms.to_json()

class MatchResource(object):
    def on_get(self, req, resp):
        matches = Match.objects.all()
        resp.body = matches.to_json()

class UserResource(object):
    def on_get(self, req, resp):
        users = User.objects.all()
        resp.body = users.to_json()

api = application = falcon.API()
api.add_route('/job-openings/', JobOpeningResource())
api.add_route('/job-seekers/', JobSeekerResource())
api.add_route('/firms/', FirmResource())
api.add_route('/matches/', MatchResource())
api.add_route('/users/', UserResource())
api.add_route('/job-match/', JobMatchResource())
api.add_route('/scores/', ScoresResource())
