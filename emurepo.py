from contextlib import contextmanager
from threading import RLock

from agent_adapter import AgentAdapter


EMU = None
LOCK = RLock()


@contextmanager
def owned_emu():
    with LOCK:
        yield EMU


@contextmanager
def owned_agent():
    with owned_emu() as emu:
        yield AgentAdapter(emu)

