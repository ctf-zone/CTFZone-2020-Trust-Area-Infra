# -*- coding: utf-8 -*-
import json
from flask import Flask, request, Blueprint
from functools import wraps
from threading import Lock


from pending_shit import notify_push_of, new_pending_request, resume_pending_request
from handlers import *
from answers import Ok, Err, Exc


SECRET_PREFIX = '/f6bd34bb2796a190bebbce5f38d71484'


def intercept_exceptions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as ex:
            return Exc(str(ex))
    return wrapper


def consumes_json(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        data = json.loads(request.data)
        return fn(data=data)
    return wrapper


api =  Blueprint('api', __name__)
api_get = lambda path: api.route(path, methods=['GET'])
api_post = lambda path: api.route(path, methods=['POST'])


@api_get('/ping')
def ping():
    return "pong"


@api_get('/status')
def status():
    # return Queue status ...
    # return Android VM status ...
    return "status"


@api_post('/answer')
@intercept_exceptions
@consumes_json
def answer(*, data):
    return handle_answer(data)


@api_post('/log_answer')
@intercept_exceptions
@consumes_json
def log_answer(*, data):
    print(data)
    return Ok()


@api_post('/echo')
@intercept_exceptions
@consumes_json
def echo(*, data):
    team, message = data['team'], data['message']
    return handle_echo(team, message)


@api_post('/push_flag')
@intercept_exceptions
@consumes_json
def push_flag(*, data):
    team, flag = data['team'], data['flag']
    new_round = data.get('new_round', False)
    user_info = data['user_info']
    description = data['description']

    if new_round:
        # notify_push_of = lambda *args: True  # MOCK !!!
        may_run = notify_push_of(team)  # block here
        if not may_run:
            return Err('Cancelled')

    return handle_push_flag(team, flag, user_info, description)


@api_post('/pull_flag')
@intercept_exceptions
@consumes_json
def pull_flag(*, data):
    team, session, task, solution = data['team'], data['session'], data['task'], data['solution']
    return handle_pull_flag(team, session, task, solution)


@api_post('/reg_user')
@intercept_exceptions
@consumes_json
def reg_user(*, data):
    team, user_info = data['team'], data['user_info']
    return handle_reg_user(team, user_info)


@api_post('/check_backup')
@intercept_exceptions
@consumes_json
def check_backup(*, data):
    team, session = data['team'], data['session']
    return handle_check_backup(team, session)


app = Flask(__name__)
app.register_blueprint(api, url_prefix=SECRET_PREFIX)


def start_webapp(host, port, **options):
    from threading import Thread
    from functools import partial

    Thread(target=partial(
        app.run,
        host=host,
        port=port,
        **options
    )).start()



if __name__ == '__main__':
    start_webapp('0.0.0.0', 31337)


