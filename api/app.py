import falcon
import json
import requests
import os

from requests.auth import HTTPBasicAuth
from mongoengine import connect

from models import JobOpening

COMMCARE_USERNAME = os.environ.get('COMMCARE_USERNAME')
COMMCARE_PASSWORD = os.environ.get('COMMCARE_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')
DB_SSL = os.environ.get('DB_SSL')
DB_HOST = os.environ.get('DB_HOST')
CASES_URL = 'https://www.commcarehq.org/a/billy-excerpt/api/v0.5/case/'


connect(db=DB_NAME, host=DB_HOST, port=int(DB_PORT), username=DB_USER, password=DB_PASSWORD)


class JobOpeningResource(object):

    def on_get(self, req, resp):
        openings = JobOpening.objects.all()

        resp.body = openings.to_json()

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200


api = application = falcon.API()

job_opening_resource = JobOpeningResource()
api.add_route('/job_opening/', job_opening_resource)
