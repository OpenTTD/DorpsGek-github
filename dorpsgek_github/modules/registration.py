import logging

from dorpsgek_github.core.helpers.aiohttp_ws import WSIsGone
from dorpsgek_github.core.processes import runner
from dorpsgek_github.core.processes.github import (
    add_installation,
    remove_installation,
    router as github,
)
from dorpsgek_github.core.processes.runner import (
    add_runner,
    remove_runner,
)

log = logging.getLogger(__name__)


@github.register("installation", action="created")
async def installation_created(event, github_api):
    add_installation(event.data["installation"]["id"])


@github.register("installation", action="deleted")
async def installation_deleted(event, github_api):
    remove_installation(event.data["installation"]["id"])


@github.register("installation_repositories", action="added")
async def installation_repositories_added(event, github_api):
    # Placeholder to have all relevant endpoints already defined.
    # Currently we don't track the exact repository we have access to, so no need to do anything.
    pass


@github.register("installation_repositories", action="removed")
async def installation_repositories_removed(event, github_api):
    # Placeholder to have all relevant endpoints already defined
    # Currently we don't track the exact repository we have access to, so no need to do anything.
    pass


@runner.register("register")
async def register(event, runner_ws):
    add_runner(runner_ws, event.data["environment"])
    await runner_ws.send_event("registered")


@runner.register("close")
async def close(event, runner_ws):
    remove_runner(runner_ws)
    await runner_ws.close()


@runner.register("error")
async def error(event, runner_ws):
    if "command_does_not_exist" in event.data:
        log.error("Runner does not support command '%s'", event.data["command_does_not_exist"])
    else:
        log.error("Unknown error received from runner")

    raise WSIsGone
