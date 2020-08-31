from threading import Thread
from time import sleep
from subprocess import run
from datetime import datetime

import emurepo
from pending_shit import wait_first_push


def start_switcher(*, team_count, on_bootstrap, log):
    log = log.getChild('EmuReloader')
    def _switcher():
        while True:
            wait_for_pushes = wait_first_push(team_count, log)
            log.info('GOT FIRST PUSH')
            resume_pushes = wait_for_pushes()
            log.info('GOT ALL PUSHES')
            with emurepo.owned_emu() as emu:
                emu.reset()
                sleep(3)
                on_bootstrap(emu)
            resume_pushes()

            iso_dt = datetime.now().isoformat()
            for idx in range(1, team_count+1):
                p = run(['bash', './save_apk.sh', str(idx), iso_dt])
                log.info(f'Team#{idx} APK saved to {iso_dt}.apk')

    Thread(target=_switcher).start()



def start_switcher2(emu1, emu2, *, team_count, on_prepare, on_bootstrap, log):
    with emurepo.owned_emu():
        emurepo.EMU = emu1
        switcher = EmuSwitcher(
            emu1, emu2,
            team_count=team_count,
            on_prepare=on_prepare,
            on_bootstrap=on_bootstrap,
            log=log,) 
        on_prepare(emu1)
        on_prepare(emu2)
        on_bootstrap(emu1)

        switcher.start()
    return switcher


class EmuSwitcher2(Thread):
    def __init__(self, emu1, emu2, *, team_count, on_prepare, on_bootstrap, log):
        super().__init__()
        self.active = True
        self.emu1 = emu1
        self.emu2 = emu2
        self.on_prepare = on_prepare
        self.on_bootstrap = on_bootstrap
        self.team_count = team_count
        self.log = log.getChild('EmuSwitcher')

    def run(self):
        cur_emu = self.emu1
        next_emu = self.emu2

        while self.active:
            # wait first
            wait_for_pushes = wait_first_push(self.team_count, self.log)
            self.log.info('GOT FIRST PUSH')
            # wait others (with emu locked)
            resume_pushes = wait_for_pushes()
            self.log.info('GOT ALL PUSHES')
            with emurepo.owned_emu():
                # semantic definitions
                emu_to_prepare = cur_emu  # will be prepared for next iteration
                emu_to_bootstrap = next_emu  # will be bootstraped soon

                # swap before critical actions
                cur_emu, next_emu = next_emu, cur_emu

                # patch global EMU
                emurepo.EMU = emu_to_bootstrap

                # bootstrap next emu
                self.bootstrap(emu_to_bootstrap)

                # run preparation in background
                # (after bootstrap to speed up)
                Thread(target=self.prepare, args=(emu_to_prepare,)).start()
            resume_pushes()

    def prepare(self, emu):
        sleep(15)
        emu.reset()
        sleep(5)
        self.on_prepare(emu)

    def bootstrap(self, emu):
        self.on_bootstrap(emu)


