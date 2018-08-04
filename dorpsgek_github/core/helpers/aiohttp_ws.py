import logging
import os

from aiohttp import (
    web,
    web_response,
    WSMsgType,
)
from asyncio import (
    CancelledError,
    Queue,
)

log = logging.getLogger(__name__)


# This bug has been fixed upstream, but not in any release yet
# https://github.com/aio-libs/aiohttp/pull/3107
def web_response_eq(self, other):
    return self is other
web_response.StreamResponse.__eq__ = web_response_eq  # noqa


class WSIsGone(Exception):
    """Thrown is the WebSocket is gone while it was doing something."""


class WSEvent:
    """Event that comes from a websocket."""
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


async def ws_send_event(self, event, data=None):
    """Easy helper function to send an event over the wire."""
    payload = {
        "type": event,
    }
    if data:
        payload["data"] = data

    await self.send_json(payload)
web.WebSocketResponse.send_event = ws_send_event  # noqa


async def ws_send_request(self, event, data=None):
    """Easy helper function to send a request over the wire, while waiting for a response."""
    payload = {
        "type": event,
    }
    if data:
        payload["data"] = data

    await self.send_event("request", payload)
    response = await self.request_response_queue.get()
    if response is WSIsGone:
        raise WSIsGone
    return response
web.WebSocketResponse.send_request = ws_send_request  # noqa


async def ws_send_artifact(self, artifact_name, filename):
    """Easy helper function to send an artifact to a websocket."""
    filesize = os.stat(filename).st_size
    data = {
        "name": artifact_name,
        "size": filesize,
    }

    await self.send_event("artifact.transfer", data)

    # Send file in chunks of 1 KiB
    with open(filename, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            await self.send_bytes(data)

    return await self.send_request("artifact.transfer_done")
web.WebSocketResponse.send_artifact = ws_send_artifact  # noqa


WS_CLOSE_EVENT = WSEvent("close")


async def ws_handler(request, process_request):
    """
    Handles a request to the HTTP server.

    This should always be a WebSocket request.
    We setup the WebSocket, and read any event that is sent over the WebSocket.
    """

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    ws.request_response_queue = Queue(maxsize=1)
    # Tell the status he is welcome.
    await ws.send_event("welcome")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                raw = msg.json()
                event = WSEvent(raw["type"], raw.get("data"))

                # "response" replies are special, and part of the request/response.
                if event.type == "response":
                    await ws.request_response_queue.put(event.data)
                else:
                    await process_request(event, ws)
            elif msg.type == WSMsgType.ERROR:
                log.error("Runner connection closed with exception", ws.exception())
                await process_request(WS_CLOSE_EVENT, ws)
                break
            else:
                log.error(f"Unexpected message type {msg.type}")
                break
    except CancelledError:
        # This is the other side terminating the connection
        await process_request(WS_CLOSE_EVENT, ws)
    except WSIsGone:
        await process_request(WS_CLOSE_EVENT, ws)
    except Exception:
        log.exception("Failed to handle runner event!")
        await process_request(WS_CLOSE_EVENT, ws)

    return ws
