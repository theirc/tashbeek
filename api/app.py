import falcon
import json
import requests
import os

from requests.auth import HTTPBasicAuth
from mongoengine import connect

from models import JobOpening
from const import connect_db


COMMCARE_USERNAME = os.environ.get('COMMCARE_USERNAME')
COMMCARE_PASSWORD = os.environ.get('COMMCARE_PASSWORD')
CASES_URL = 'https://www.commcarehq.org/a/billy-excerpt/api/v0.5/case/'

connect_db()

class JobOpeningResource(object):

    def on_get(self, req, resp):
        openings = JobOpening.objects.all()

        resp.body = openings.to_json()

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200


class HelloWorldResource(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('hello world!')

api = application = falcon.API()

job_opening_resource = JobOpeningResource()
hello_world_resource = HelloWorldResource()
api.add_route('/job_opening/', job_opening_resource)
api.add_route('/', hello_world_resource)
