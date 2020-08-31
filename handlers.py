from functools import wraps

from answers import Ok, Err, Raw

from emurepo import owned_emu, owned_agent
from pending_shit import new_pending_request, resume_pending_request


def handle_answer(data):
    req_id = data.get('__req_id__')
    if req_id is None:
        raise Exception(f'NO req_id in data={data}')
    del data['__req_id__']
    if req_id == '__print__':
        print(data)
    elif req_id == '__skip__':
        pass
    else:
        resume_pending_request(req_id, data)
    return Ok()


def awaits_and_returns_raw(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        req_id, wait = new_pending_request()
        with owned_agent() as agent:
            fn(*args, req_id=req_id, agent=agent, **kwargs)
        data = wait()
        return Raw(data)
    return wrapper


@awaits_and_returns_raw
def handle_echo(team, message, *, req_id, agent):
    agent.echo(req_id, team, message)


@awaits_and_returns_raw
def handle_push_flag(team, flag, user_info, description, *, req_id, agent):
    agent.push_flag(req_id, team, flag, user_info, description)


@awaits_and_returns_raw
def handle_pull_flag(team, session, task, solution, *, req_id, agent):
    agent.pull_flag(req_id, team, session, task, solution)


@awaits_and_returns_raw
def handle_reg_user(team, user_info, *, req_id, agent):
    agent.reg_user(req_id, team, user_info)


@awaits_and_returns_raw
def handle_check_backup(team, session, *, req_id, agent):
    agent.check_backup(req_id, team, session)

