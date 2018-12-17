from mongoengine import DynamicDocument, StringField

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
