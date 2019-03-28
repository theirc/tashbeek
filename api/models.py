from mongoengine import (DynamicDocument, StringField, Document, DateTimeField)

class JobOpening(DynamicDocument):
    case_id = StringField(required=True, unique=True)
    job_id = StringField(required=True, unique=True)

class JobMatch(DynamicDocument):
    job_id = StringField(required=True, unique=True)

class JobSeeker(DynamicDocument):
    case_id = StringField(required=True, unique=True)

class Firm(DynamicDocument):
    case_id = StringField(required=True, unique=True)

class Match(DynamicDocument):
    case_id = StringField(required=True, unique=True)

class User(DynamicDocument):
    user_id = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)

class ThompsonProbability(Document):
    date = DateTimeField(required=True)
    probs = StringField(required=True)

class Cron(Document):
    date = DateTimeField(required=True)
    status = StringField(required=True)
    cron_type = StringField(required=True)
    error = StringField(default='')
    thompson_output = StringField(default='')
