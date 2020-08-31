from emuman import Emulator, EnvConfig, InstallConfig
from functools import partial
from threading import Thread
import logging
import sys


def init_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s |  %(message)s'
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)


init_logger()


def deploy(emu: Emulator, install_config: InstallConfig):
    deploy_pipeline = (
        emu.reset,
        partial(emu.install_multiple_apks, install_config.admin_apks),
        partial(emu.install_multiple_apks, install_config.players_apks),
    )
    for stage in deploy_pipeline:
        ok = stage()
        if not ok:
            return False
    # TODO: start some service
    # emu.start_service('some.package', 'some.class.Path', action='some.action', extras={'some.extra.name': 'some.extra.value'})
    return True


def Emu1():
    return Emulator(
        'ctfz.trustarea.device1',
        snapshot='KLEAN',
        console_port=5574,
        env_config=EnvConfig()
    )


def Team1():
    return Emulator(
        'ctfz.trustarea.device1',
        snapshot='TEAM1',
        console_port=5574,
        env_config=EnvConfig()
    )


def AA4Team1():
    emu = Team1()
    emu.start()
    from agent_adapter import AgentAdapter
    aa = AgentAdapter(emu)
    return emu, aa


def Emu2():
    return Emulator(
        'ctfz.trustarea.device2',
        snapshot='KLEAN',
        console_port=5584,
        env_config=EnvConfig()
    )


def StartedEmu1():
    emu = Emu1()
    emu.start()
    return emu

def StartedEmu2():
    emu = Emu2()
    emu.start()
    return emu

def StartedEmus():
    return StartedEmu1(), StartedEmu2()


def SrvWithEmu():
    import emurepo
    from api import app

    with emurepo.owned_emu():
        emu = Team1()
        emu.start()
        emurepo.EMU = emu

    def background_api():
        try:
            app.run(host='172.16.92.133', port=31337)
        except KeyboardInterrupt:
            print('STOPPING !!!!!1')
        except Exception:
            print('FAILED BLYA:', str(ex))

        with emurepo.owned_emu() as emu:
            emu.kill()

    Thread(target=background_api).start()

    return emurepo.owned_emu


def AA4Team1Api():
    emu, aa = AA4Team1()
    from api import app
    Thread(target=partial(app.run, host='172.16.92.133', port=31337)).start()
    return emu, aa


def PullSc():
    emu, aa = AA4Team1Api()
    import emurepo
    emurepo.EMU = emu
    return emu, aa


