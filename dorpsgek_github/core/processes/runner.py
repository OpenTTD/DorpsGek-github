import asyncio
import logging
import random

from collections import defaultdict

log = logging.getLogger(__name__)

_registry = defaultdict(list)
_runners = defaultdict(list)


class RunnerEventDoesntExist(Exception):
    """Thrown if the event given to process doesn't have any handlers."""


class NoRunnerException(Exception):
    """"Thrown if there was no runner for the given environment."""


class RunnerIsGone(Exception):
    """Thrown is the runner is gone while it was doing something."""


async def process_request(event, ws):
    """
    Process a single request.
    """

    if not len(_registry[event.type]):
        raise RunnerEventDoesntExist(event.type)

    for func in _registry[event.type]:
        await func(event, ws)


def register(command):
    """Register an event for the runner."""

    def wrapped(func):
        _registry[command].append(func)
        return func
    return wrapped


def add_runner(runner_ws, environment):
    """Add a runner for a specific environment."""

    log.info("New runner for environment '%s'", environment)
    runner_ws.claimed = False
    _runners[environment].append(runner_ws)


def remove_runner(runner_ws):
    """Remove a specific runner from all environments. """

    for env in _runners.keys():
        try:
            _runners[env].remove(runner_ws)
            log.info("Lost runner for environment '%s'", env)
        except ValueError:
            pass

    # Notify anything blocking in request/response about the removal
    runner_ws.request_response_queue.put_nowait(RunnerIsGone)


class RunnerContext:
    """
    A context to claim a runner for a given job.

    While the runner is claimed, no other job can claim the runner.
    It will block if no runners are currently available.
    """
    def __init__(self, environment):
        self._environment = environment

    async def __aenter__(self):
        if not len(_runners[self._environment]):
            raise NoRunnerException(self._environment)

        # Wait for any runner to become available
        while True:
            available_runners = [runner for runner in _runners[self._environment] if runner.claimed is False]
            if len(available_runners):
                break
            await asyncio.sleep(1)

        self._runner = random.choice(available_runners)
        self._runner.claimed = True
        return self._runner

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._runner.claimed = False
