from queue import Queue
from threading import Lock
from uuid import uuid4
from time import sleep, time


def new_id():
    return str(uuid4())


def make_pause():
    q = Queue(maxsize=1)
    return q.get, q.put


# Pushes "API"
PUSH_QUEUE = Queue()

def notify_push_of(team):
    wait, resume = make_pause()
    PUSH_QUEUE.put((team, resume))
    may_run = wait()
    return may_run


def wait_first_push(n, log):
    resumes = []
    teams = set()
    first, resume = PUSH_QUEUE.get()
    teams.add(first)
    resumes.append(resume)
    log.info(f'PUSH FROM TEAM#{first}')

    def wait_for_pushes():
        while len(teams) < 10:
            team, resume = PUSH_QUEUE.get()
            teams.add(team)
            resumes.append(resume)

        def _resume_pushes():
            for resume in resumes:
                resume(True)
        return _resume_pushes
    return wait_for_pushes


# Answers "API"
PENDING_REQUESTS = {}
REQ_LOCK = Lock()


def new_pending_request():
    req_id = new_id()
    wait, resume = make_pause()
    with REQ_LOCK:
        PENDING_REQUESTS[req_id] = (time(), resume)
    return req_id, wait


def resume_pending_request(req_id, data):
    with REQ_LOCK:
        if req_id in PENDING_REQUESTS:
            _, resume = PENDING_REQUESTS[req_id]
            del PENDING_REQUESTS[req_id]
        else:
            raise Exception(f'Unknown req_id={req_id} in {data}')
    resume(data)


DROPPER_DELAY = 5
DROPPER_TIMEOUT = 60 * 5
def dropper():
    from answers import Err
    import logging
    log = logging.getLogger().getChild('DROPPER')
    DATA = {'status': 'error', 'error': 'timeout: generic'}
    while True:
        try:
            sleep(DROPPER_DELAY)
            with REQ_LOCK:
                to_delete = []
                for req_id, value in PENDING_REQUESTS.items():
                    moment, resume = value
                    if time() - moment > DROPPER_TIMEOUT:
                        log.info(req_id)
                        to_delete.append(req_id)
                        resume(DATA)
                for req_id in to_delete:
                    del PENDING_REQUESTS[req_id]
        except Exception as ex:
            log.error(f'error: {ex!r}')

from threading import Thread
Thread(target=dropper).start()
