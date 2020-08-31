import subprocess
import logging
from threading import Thread, RLock
from dataclasses import dataclass
from pathlib import Path
from typing import List
from itertools import chain
from functools import wraps
from time import sleep
from contextlib import contextmanager


def obj_addr(obj):
    return hex(id(obj))[2:]


def prettify_line(byte_line):
    return byte_line.decode().strip()


def make_shell_string(args):
    return ' '.join(chain(('$',), map(str, args)))


def log_action(action_name, extra=''):
    def _log_action(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            self = args[0]
            old_log = self._log

            mark = object()
            log = old_log.getChild(obj_addr(mark))

            self._log = log  # for a while

            log.info(f'{action_name} {extra.format(*args, **kwargs)} STARTED')
            ok = method(*args, **kwargs)
            if ok:
                log.info(f'{action_name} {extra.format(*args, **kwargs)} OK')
            else:
                log.error(f'{action_name} {extra.format(*args, **kwargs)} FAILED')

            self._log = old_log  # reverting
            return ok
        return wrapper
    return _log_action


@dataclass
class EnvConfig:
    adb_path: Path = Path('adb')
    emu_path: Path = Path('emulator')


@dataclass
class InstallConfig:
    admin_apks: List[Path]
    players_apks: List[Path]


def run(args, **options):
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **options)


def log_stdout(sub, *, logger):
    while sub.poll() is None:
        line = prettify_line(sub.stdout.readline())
        if line:
            logger.info(line)
    return sub.poll() == 0


def run_and_log(args, *, logger, **options):
    logger.info(make_shell_string(args))
    return log_stdout(run(args, **options), logger=logger)


def if_alive(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.is_alive:
            return method(self, *args, **kwargs)
        else:
            self._log.error('Emulator is not alive')
            return False
    return wrapper


def thread_safe(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self.owned():
            return method(self, *args, **kwargs)
    return wrapper


class Emulator:
    def __init__(self, avd_name: str, *, snapshot: str, console_port: int, env_config: EnvConfig):
        self._emu = None
        self._lock = RLock()  # required for `thread_safe`

        self._snapshot = snapshot

        self._emu_args = (
            env_config.emu_path,
            '-avd', avd_name,
            '-port', str(console_port),
            '-no-boot-anim',
            # '-no-window'
        )

        self._adb_prefix = (env_config.adb_path, '-s', f'emulator-{console_port}')

        self._log = logging.getLogger(f'emu-{console_port}-{obj_addr(self)}')
        self._log.setLevel(logging.INFO)

    def __repr__(self):
        return f'{self.__class__.__name__}@{obj_addr(self)}'

    def __del__(self):
        if self.is_alive:
            self.kill()

    @contextmanager
    def owned(self):
        with self._lock:
            yield

    @property
    def is_alive(self):
        return self._emu is not None and self._emu.poll() is None

    def run_adb(self, *options):
        args = tuple(chain(self._adb_prefix, options))
        return run_and_log(args, logger=self._log)

    @thread_safe
    def start(self):
        self._log.info('Start running...')
        mark = object()
        addr = obj_addr(mark)
        run_logger = self._log.getChild('EMU_PROC')

        run_logger.info(make_shell_string(self._emu_args))
        emu = run(self._emu_args)

        self._emu = emu

        # wait emulator to init
        booted = self.wait_boot()
        if not booted:
            return False

        def back_task():
            ok = log_stdout(emu, logger=run_logger)
            if ok:
                run_logger.info('[FINISHED]')
            else:
                run_logger.error('[FAILED]')

        Thread(target=back_task).start()

        return self.is_alive and self.reset()

    @thread_safe
    @log_action('Pausing')
    def pause(self):
        return self.run_adb('emu', 'avd', 'pause')

    @thread_safe
    @log_action('Resuming')
    def resume(self):
        result = self.run_adb('emu', 'avd', 'resume')
        sleep(0.2)
        return result

    @property
    def is_boot_completed(self):
        args = tuple(chain(self._adb_prefix, ('shell', 'getprop', 'sys.boot_completed')))
        sub = run(args)
        verdict = False
        while sub.poll() is None:
            line = prettify_line(sub.stdout.readline())
            if line.strip() == '1':
                verdict = True
        return verdict

    def wait_boot(self, *, delay=1):
        while self.is_alive and not self.is_boot_completed:
            sleep(delay)
        return self.is_alive and self.is_boot_completed

    @thread_safe
    @log_action('Killing')
    @if_alive
    def kill(self):
        return self.run_adb('emu', 'kill')

    @thread_safe
    @log_action('Reset')
    @if_alive
    def reset(self):
        return self.run_adb('emu', 'avd', 'snapshot', 'load', self._snapshot)

    @thread_safe
    @log_action('Installing', extra='package={1}')
    @if_alive
    def install(self, apk_path):
        return self.run_adb('install', '-r', apk_path)

    @thread_safe
    @log_action('Installing multiple', extra='packages={1!r}')
    def install_multiple(self, apk_paths):
        return all(map(self.install, apk_paths))

    @thread_safe
    @log_action('Starting service', extra='{1}/{2}')
    @if_alive
    def start_service(self, package, class_path, *, action=None, extras=None):
        args = ['shell', 'am', 'startservice']
        if action is not None:
            args.extend(('-a', str(action)))
        if extras is not None:
            for name, value in extras.items():
                args.extend(('-e', str(name), str(value)))
        target = f'{package}/{class_path}'
        args.append(target)
        return self.run_adb(*args)


