from gevent import monkey
monkey.patch_all()
import gevent
import falcon
import json
import requests
import os
import operator

from requests.auth import HTTPBasicAuth
from mongoengine import connect, DoesNotExist
from falcon_auth import FalconAuthMiddleware, TokenAuthBackend

from models import JobOpening, JobSeeker, Firm, Match, User, JobMatch
from const import connect_db, disconnect_db
from utils import create_match_object

COMMCARE_USERNAME = os.environ.get('COMMCARE_USERNAME')
COMMCARE_PASSWORD = os.environ.get('COMMCARE_PASSWORD')
CASES_URL = 'https://www.commcarehq.org/a/billy-excerpt/api/v0.5/case/'

def init_db(req, resp, resource, kwargs=None):
    connect_db()


def tear_down_db(req, resp, resource, kwargs=None):
    disconnect_db()

class JobMatchResource(object):

    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_get(self, req, resp):
        job_id = req.params['job_id']
        try:
            match = JobMatch.objects.get(job_id=job_id)
            if hasattr(match, 'scores'):
                match.scores.sort(key=operator.itemgetter('probs'))
            resp.body = match.to_json()
        except DoesNotExist:
            resp.status = falcon.HTTP_404

    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_delete(self, req, resp):
        job_id = req.params['job_id']
        if not JobOpening.objects(job_id=job_id):
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({
                "code": 400,
                "message": "Job Opening with ID does not exist.",
                "more_info": "https://nolski.github.io/tashbeek#job-match-job-matches-post-2"
            })
            return

        try:
            match = JobMatch.objects.get(job_id=job_id)
            match.delete()
            resp.status = falcon.HTTP_204
        except DoesNotExist:
            resp.status = falcon.HTTP_404

    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_post(self, req, resp):
        job_id = req.params['job_id']
        if not JobOpening.objects(job_id=job_id):
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({
                "code": 400,
                "message": "Job Opening with ID does not exist.",
                "more_info": "https://nolski.github.io/tashbeek#job-match-job-matches-post-2"
            })
            return

        try:
            match = JobMatch.objects.get(job_id=job_id)
            resp.status = falcon.HTTP_409
            if hasattr(match, 'scores'):
                match.scores.sort(key=operator.itemgetter('probs'))
            resp.body = match.to_json()
        except DoesNotExist:
            gevent.spawn(create_match_object, job_id)
            resp.status = falcon.HTTP_201

class JobOpeningResource(object):
    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_get(self, req, resp):
        openings = JobOpening.objects.all()
        resp.body = openings.to_json()

class JobSeekerResource(object):
    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_get(self, req, resp):
        job_seekers = JobSeeker.objects.all()
        resp.body = job_seekers.to_json()

class FirmResource(object):
    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_get(self, req, resp):
        firms = Firm.objects.all()
        resp.body = firms.to_json()

class MatchResource(object):
    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_get(self, req, resp):
        matches = Match.objects.all()
        resp.body = matches.to_json()

class UserResource(object):
    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_get(self, req, resp):
        users = User.objects.all()
        resp.body = users.to_json()

class HomeResource(object):
    @falcon.before(init_db)
    @falcon.after(tear_down_db)
    def on_get(self, req, resp):
        resp.body = '{"hello": "world"}'

def user_loader(token):
    password = os.environ.get('AUTH_TOKEN', None)
    if token == password:
        return {'id': 1}
    else:
        return None

token_auth = TokenAuthBackend(user_loader=user_loader)
auth_middleware = FalconAuthMiddleware(token_auth)
api = application = falcon.API(middleware=[auth_middleware])
api.add_route('/job-openings/', JobOpeningResource())
api.add_route('/job-seekers/', JobSeekerResource())
api.add_route('/firms/', FirmResource())
api.add_route('/matches/', MatchResource())
api.add_route('/users/', UserResource())
api.add_route('/job-matches/', JobMatchResource())
api.add_route('/', HomeResource())
