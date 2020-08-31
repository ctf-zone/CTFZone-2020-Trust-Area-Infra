import sys
import logging
import logging.handlers


def init(place=None):
    # TODO: log to file
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if place is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.handlers.RotatingFileHandler(
            place, 
            maxBytes=10 * 1024 * 1024,
            backupCount=10
        )
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s |  %(message)s'
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    return root


