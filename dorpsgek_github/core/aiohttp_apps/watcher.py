import logging

from dorpsgek_github.core.helpers.aiohttp_ws import ws_handler
from dorpsgek_github.core.processes import watcher

log = logging.getLogger(__name__)


async def watcher_handler(request):
    """
    Handles a request to the watcher HTTP server.
    """

    await ws_handler(request, watcher.process_request)
