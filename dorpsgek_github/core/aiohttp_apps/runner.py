import logging

from dorpsgek_github.core.helpers.aiohttp_ws import ws_handler
from dorpsgek_github.core.processes import runner

log = logging.getLogger(__name__)


async def runner_handler(request):
    """
    Handles a request to the Runner HTTP server.
    """

    await ws_handler(request, runner.process_request)
