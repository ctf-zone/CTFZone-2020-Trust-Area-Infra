from subprocess import run
from time import sleep
from threading import Thread


def start_grabber(team2back, *, delay=60, log):
    log = log.getChild('GRABBER')
    def _grab_forever():
        while True:
            try:
                sleep(delay)
                log.info('Start grabbing')
                for team, back in team2back.items():
                    p = run(['bash', './grab_apk.sh', str(team), str(back)])
                    log.info(f'Team#{team}@{back} ret={p.returncode}')
            except Exception as ex:
                log.error(ex)
    Thread(target=_grab_forever).start()
