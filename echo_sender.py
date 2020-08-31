from threading import Thread
from time import sleep

from emurepo import owned_agent


def start_echo_sender(*, delay, team_count, log):
    log = log.getChild('ECHO')
    def _echo_sender():
        while True:
            sleep(delay)
            log.info('Start ...')
            try:
                with owned_agent() as agent:
                    for team in range(1, team_count+1):
                        agent.echo('__skip__', team, 'pulse')
                log.info('Finished!')
            except Exception as ex:
                log.error(f'Failed: {ex!r}')
    Thread(target=_echo_sender).start()
