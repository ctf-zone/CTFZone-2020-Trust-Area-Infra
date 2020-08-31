import json


def Raw(data):
    return json.dumps(data)


def Ans(status, **message):
    return Raw({
        'status': status,
        **message
    })

def Ok(**message):
    return Ans('ok', message)


def Err(message):
    return Ans('error', error=message)


def Exc(message):
    return Ans('exception', error=message)


