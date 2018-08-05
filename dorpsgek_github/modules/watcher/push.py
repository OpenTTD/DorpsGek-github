import yaml

from dorpsgek_github import config
from dorpsgek_github.core.helpers.github import get_dorpsgek_yml
from dorpsgek_github.core.processes import watcher
from dorpsgek_github.core.processes.github import router as github


@github.register("push")
async def push(event, github_api):
    branch = event.data["ref"]
    ref = event.data["head_commit"]["id"]
    repository_name = event.data["repository"]["full_name"]

    commits = [
        {
            "message": commit["message"],
            "author": commit["author"]["username"],
        }
        for commit in event.data["commits"]
    ]
    user = event.data["pusher"]["name"]

    if len(event.data["commits"]) > 1:
        url = event.data["compare"]
    else:
        # Strip 28 chars from the sha-hash, to make the URL shorter
        url = event.data["commits"][0]["url"][:-28]

    # Only notify about pushes to heads; not to tags etc
    if not branch.startswith("refs/heads/"):
        return

    branch = branch[len("refs/heads/"):]

    payload = {
        "repository_name": repository_name,
        "user": user,
        "url": url,
        "branch": branch,
        "ref": ref,
        "commits": commits,
    }

    # Get the .dorpsgek.yml, so we know what to do
    raw_yml = await get_dorpsgek_yml(github_api, repository_name, ref)
    if raw_yml:
        yml = yaml.load(raw_yml)
        services = yml["notifications"].get("push", {})

        for protocol, userdata in services.items():
            payload["userdata"] = userdata
            await watcher.send_to_watchers(protocol, "notify.push", payload)

    for protocol, userdata in config.NOTIFICATIONS_DICT.items():
        payload["userdata"] = userdata
        await watcher.send_to_watchers(protocol, "notify.push", payload)

