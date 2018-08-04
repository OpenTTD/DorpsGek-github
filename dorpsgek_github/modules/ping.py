from dorpsgek_github.core.processes import (
    runner,
    watcher,
)
from dorpsgek_github.core.processes.github import router as github


@github.register("ping")
async def github_ping(event, github_api):
    # By simply doing nothing, we will return an OK on the ping.
    # This is all GitHub would like to see. No further action needed.
    pass


@runner.register("ping")
async def runner_ping(event, runner_ws):
    await runner_ws.send_event("pong", {"time": event.data["time"]})


@watcher.register("ping")
async def watcher_ping(event, watcher_ws):
    await watcher_ws.send_event("pong", {"time": event.data["time"]})
