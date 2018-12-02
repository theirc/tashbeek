import requests

from const import connect_db
from models import User

USERS_URL = 'https://www.commcarehq.org/a/billy-excerpt/api/v0.5/user/'
DROPBOX_URL = 'https://www.dropbox.com/s/p0jdw71vwu1quru/scores.csv?dl=1'

def pretty_print_request(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

def set_probabilities() -> None:
    r = requests.get(DROPBOX_URL)
    print('getting probabilities...')
    probabilities = r.content.decode().split('\n')[1]
    print('getting users...')
    users = User.objects.all()
    for user in users:
        if 'eso' not in user['username']:
            continue
        user['user_data']['treatment_probabilities'] = probabilities
        print(f"putting data for {user['username']}...")
        user_dict = dict(user.to_mongo())
        user_dict.pop('_id')

        req = requests.Request('PUT', USERS_URL + user.user_id, json=user_dict)
        prepared = req.prepare()
        pretty_print_request(prepared)

        requests.put(USERS_URL + user.user_id, json=user_dict)

if __name__ == '__main__':
    connect_db()
    print('setting probabilities...')
    set_probabilities()
