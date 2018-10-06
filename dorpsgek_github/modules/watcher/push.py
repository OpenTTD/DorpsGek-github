import re
import yaml

from dorpsgek_github import config
from dorpsgek_github.core.helpers.github import get_dorpsgek_yml
from dorpsgek_github.core.processes import watcher
from dorpsgek_github.core.processes.github import router as github


# If set to a sha, this sha will be ignored once if seen on a push.
# Used to not show both a Pull Request merge as a Push about the PR.
ignore_next_push_sha = None


@github.register("push")
async def push(event, github_api):
    global ignore_next_push_sha

    branch = event.data["ref"]
    ref = event.data["head_commit"]["id"]
    repository_name = event.data["repository"]["full_name"]

    # If we were asked to ignore this sha, do that once
    if ignore_next_push_sha and event.data["after"] == ignore_next_push_sha:
        ignore_next_push_sha = None
        return

    commits = [
        {
            "message": commit["message"],
            "author": commit["author"]["username"],
        }
        for commit in event.data["commits"]
    ]
    user = event.data["sender"]["login"]

    if len(event.data["commits"]) > 1:
        url = event.data["compare"]
    else:
        url = event.data["commits"][0]["url"]

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

        # Check if there was a filter in place for branches
        filter_only = yml["notifications"].get("push", {}).get("only", [])
        for filter in filter_only:
            if re.match(filter, branch):
                break
        else:
            # No match found, so we didn't match the 'only'; ignore this notification
            return

        filter_except = yml["notifications"].get("push", {}).get("except", [])
        for filter in filter_except:
            if re.match(filter, branch):
                # We match the except; ignore this notification
                return

        services = yml["notifications"].get("push", {})
        for protocol, userdata in services.items():
            # "only" and "except" are not protocols, but filters; ignore them
            if protocol in ["only", "except"]:
                continue

            payload["userdata"] = userdata
            await watcher.send_to_watchers(protocol, "notify.push", payload)

    for protocol, userdata in config.NOTIFICATIONS_DICT.items():
        payload["userdata"] = userdata
        await watcher.send_to_watchers(protocol, "notify.push", payload)
