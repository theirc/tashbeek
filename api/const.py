import os

from mongoengine import connect, DynamicDocument

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')

def connect_db():
    connect(
        db=DB_NAME,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        authentication_source='admin',
    )
