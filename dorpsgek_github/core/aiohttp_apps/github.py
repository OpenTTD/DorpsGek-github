import http
import logging

from aiohttp import web
from dorpsgek_github.core.processes import github

log = logging.getLogger(__name__)


async def github_handler(request):
    """
    Handles a request to the GitHub HTTP server.

    We read the headers and body, and set it through to process.github for further processing.
    """

    headers = request.headers
    data = await request.read()

    try:
        await github.process_request(headers, data)
        return web.Response(status=http.HTTPStatus.OK)
    except Exception:
        log.exception("Failed to handle GitHub event!")
        return web.Response(status=http.HTTPStatus.INTERNAL_SERVER_ERROR)


async def github_probe_handler(request):
    return web.Response(status=http.HTTPStatus.OK)


async def github_startup(app):
    await github.startup()
