import logging

from collections import defaultdict

from dorpsgek_github.core.helpers.aiohttp_ws import WSIsGone

log = logging.getLogger(__name__)

_registry = defaultdict(list)
_watchers = defaultdict(list)


class WatcherEventDoesntExist(Exception):
    """Thrown if the event given to process doesn't have any handlers."""


async def process_request(event, ws):
    """
    Process a single request.
    """

    if not len(_registry[event.type]):
        raise WatcherEventDoesntExist(event.type)

    for func in _registry[event.type]:
        await func(event, ws)


def register(command):
    """Register an event for the watcher."""

    def wrapped(func):
        _registry[command].append(func)
        return func
    return wrapped


def add_watcher(watcher_ws, protocol):
    """Add a watcher for a specific protocol."""

    log.info("New watcher for protocol '%s'", protocol)
    _watchers[protocol].append(watcher_ws)


def remove_watcher(watcher_ws):
    """Remove a specific watcher from all protocols."""

    for protocol in _watchers.keys():
        try:
            _watchers[protocol].remove(watcher_ws)
            log.info("Lost watcher for protocol '%s'", protocol)
        except ValueError:
            pass

    # Notify anything blocking in request/response about the removal
    watcher_ws.request_response_queue.put_nowait(WSIsGone)


async def send_to_watchers(protocol, event, data):
    for watcher_ws in _watchers[protocol]:
        await watcher_ws.send_event(event, data=data)
