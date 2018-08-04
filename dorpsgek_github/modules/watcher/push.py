import yaml

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
    pusher = event.data["pusher"]["name"]

    if len(event.data["commits"]) > 1:
        url = event.data["compare"]
    else:
        # Strip 28 chars from the sha-hash, to make the URL shorter
        url = event.data["commits"][0]["url"][:-28]

    assert branch.startswith("refs/heads/")
    branch = branch[len("refs/heads/"):]

    # Get the .dorpsgek.yml, so we know what to do
    raw_yml = await get_dorpsgek_yml(github_api, repository_name, ref)
    yml = yaml.load(raw_yml)
    if "push" not in yml["notifications"]:
        return

    services = yml["notifications"].get("push", {})
    for protocol, userdata in services.items():
        await watcher.send_to_watchers(protocol, "notify.push", {
            "userdata": userdata,
            "repository_name": repository_name,
            "branch": branch,
            "ref": ref,
            "commits": commits,
            "pusher": pusher,
            "url": url,
        })
