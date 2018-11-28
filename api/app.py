import falcon
import json
import requests
import os

from requests.auth import HTTPBasicAuth
from mongoengine import connect

from models import JobOpening, JobSeeker, Firm, Match
from const import connect_db


COMMCARE_USERNAME = os.environ.get('COMMCARE_USERNAME')
COMMCARE_PASSWORD = os.environ.get('COMMCARE_PASSWORD')
CASES_URL = 'https://www.commcarehq.org/a/billy-excerpt/api/v0.5/case/'

connect_db()

class JobOpeningResource(object):
    def on_get(self, req, resp):
        openings = JobOpening.objects.all()
        resp.body = openings.to_json()

class JobSeekerResource(object):
    def on_get(self, req, resp):
        openings = JobSeeker.objects.all()
        resp.body = openings.to_json()

class FirmResource(object):
    def on_get(self, req, resp):
        openings = Firm.objects.all()
        resp.body = openings.to_json()

class MatchResource(object):
    def on_get(self, req, resp):
        openings = Match.objects.all()
        resp.body = openings.to_json()

class HelloWorldResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('hello world!')

api = application = falcon.API()

job_opening_resource = JobOpeningResource()
job_seeker_resource = JobSeekerResource()
firm_resource = FirmResource()
match_resource = MatchResource()
hello_world_resource = HelloWorldResource()
api.add_route('/job-openings/', job_opening_resource)
api.add_route('/job-seekers/', job_seeker_resource)
api.add_route('/firms/', firm_resource)
api.add_route('/matches/', match_resource)
api.add_route('/', hello_world_resource)
