from functools import partial

from emuman import Emulator, EnvConfig, InstallConfig
from api import start_webapp
from emuswitcher import start_switcher
from apk_grabber import start_grabber
from echo_sender import start_echo_sender
import logger
from time import sleep
import emurepo


EMUS = (
    Emulator(
        'ctfz.trustarea.device1',
        snapshot='KLEAN',
        console_port=5574,
        env_config=EnvConfig()
    ),
    Emulator(
        'ctfz.trustarea.device2',
        snapshot='KLEAN',
        console_port=5584,
        env_config=EnvConfig()
    )
)


APKs_PATH = '/home/ctfzone/Desktop/APKs'
TEAM_COUNT = 10
CHECKER_COUNT = 10

INSTALL_CONFIG = InstallConfig(
    [
        #f'{APKs_PATH}/Checker{idx}.apk'
        # for idx in range(1, CHECKER_COUNT + 1)
    ], [
        f'{APKs_PATH}/Team{idx}.apk'
        for idx in range(1, TEAM_COUNT + 1)
    ]
)

TEAM2BACK = {
    idx: f'100.100.{idx}.10:7000'
    for idx in range(1, TEAM_COUNT + 1)
}

GRAB_DELAY=60


def start_emus(emus):
    return all(emu.start() for emu in emus)


def install_apks(apks, emu):
    return emu.install_multiple(apks)


def start(emu, install_config, host_port, log_path=None):
    log = logger.init(log_path)

    # stat emulators
    emu_started = emu.start()
    if not emu_started:
        log.error('Failed to start emulators')
        return False

    sleep(3)
    install_players_apks = partial(install_apks, install_config.players_apks)
    install_players_apks(emu)

    with emurepo.owned_emu():
        emurepo.EMU = emu

    # start switcher
    start_switcher(
        team_count=TEAM_COUNT,
        on_bootstrap=install_players_apks,
        log=log
    )

    # start apk grabber
    start_grabber(TEAM2BACK, delay=GRAB_DELAY, log=log)

    # start echo-pulse sender
    start_echo_sender(delay=30, team_count=TEAM_COUNT, log=log)

    # start api
    host, port = host_port
    start_webapp(host, port)

    return emu, lambda: install_players_apks(emu)


def the_show():
    return start(EMUS[0], INSTALL_CONFIG, ('0.0.0.0', 31337), '/home/ctfzone/Desktop/LOGs/event.log')

