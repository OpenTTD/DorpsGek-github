import yaml

from dorpsgek_github import config
from dorpsgek_github.core.helpers.github import get_dorpsgek_yml
from dorpsgek_github.core.processes import watcher
from dorpsgek_github.core.processes.github import router as github


async def _notify(github_api, ref, *,
                  repository_name=None,
                  user=None,
                  url=None,
                  action=None,
                  issue_id=None,
                  title=None):

    payload = {
        "repository_name": repository_name,
        "user": user,
        "url": url,
        "action": action,
        "issue_id": issue_id,
        "title": title,
    }

    # Get the .dorpsgek.yml, so we know what to do
    raw_yml = await get_dorpsgek_yml(github_api, repository_name, ref)
    if raw_yml:
        yml = yaml.load(raw_yml)

        services = yml["notifications"].get("issue", {})
        for protocol, userdata in services.items():
            payload["userdata"] = userdata
            await watcher.send_to_watchers(protocol, "notify.issue", payload)

    for protocol, userdata in config.NOTIFICATIONS_DICT.items():
        payload["userdata"] = userdata
        await watcher.send_to_watchers(protocol, "notify.issue", payload)


@github.register("issues")
async def issues(event, github_api):
    action = event.data["action"]
    repository_name = event.data["repository"]["full_name"]
    issue_id = event.data["issue"]["number"]
    title = event.data["issue"]["title"]
    url = event.data["issue"]["html_url"]
    user = event.data["issue"]["user"]["login"]

    if action not in ("opened", "closed", "reopened"):
        return

    await _notify(github_api, event.data["repository"]["default_branch"],
                  repository_name=repository_name,
                  user=user,
                  url=url,
                  action=action,
                  issue_id=issue_id,
                  title=title)


@github.register("issue_comment")
async def issue_comment(event, github_api):
    if "pull_request" in event.data["issue"]:
        return

    if event.data["action"] != "created":
        return

    repository_name = event.data["repository"]["full_name"]
    issue_id = event.data["issue"]["number"]
    title = event.data["issue"]["title"]
    url = event.data["comment"]["html_url"]
    user = event.data["comment"]["user"]["login"]

    await _notify(github_api,  event.data["repository"]["default_branch"],
                  repository_name=repository_name,
                  user=user,
                  url=url,
                  action="comment",
                  issue_id=issue_id,
                  title=title)
