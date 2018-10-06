import yaml

from dorpsgek_github import config
from dorpsgek_github.core.helpers.github import get_dorpsgek_yml
from dorpsgek_github.core.processes import watcher
from dorpsgek_github.core.processes.github import router as github
from dorpsgek_github.modules.watcher import push


async def _notify(github_api, ref, *,
                  repository_name=None,
                  user=None,
                  url=None,
                  action=None,
                  pull_id=None,
                  title=None):

    payload = {
        "repository_name": repository_name,
        "user": user,
        "url": url,
        "action": action,
        "pull_id": pull_id,
        "title": title,
    }

    # Get the .dorpsgek.yml, so we know what to do
    raw_yml = await get_dorpsgek_yml(github_api, repository_name, ref)
    if raw_yml:
        yml = yaml.load(raw_yml)

        services = yml["notifications"].get("pull-request", {})
        for protocol, userdata in services.items():
            payload["userdata"] = userdata
            await watcher.send_to_watchers(protocol, "notify.pull_request", payload)

    for protocol, userdata in config.NOTIFICATIONS_DICT.items():
        payload["userdata"] = userdata
        await watcher.send_to_watchers(protocol, "notify.pull_request", payload)


@github.register("pull_request")
async def pull_request(event, github_api):
    action = event.data["action"]
    repository_name = event.data["repository"]["full_name"]
    pull_id = event.data["pull_request"]["number"]
    title = event.data["pull_request"]["title"]
    url = event.data["pull_request"]["html_url"]
    user = event.data["sender"]["login"]

    if action not in ("opened", "synchronize", "closed", "reopened"):
        return

    if action == "closed" and event.data["pull_request"]["merged"]:
        action = "merged"
        push.ignore_next_push_sha = event.data["pull_request"]["merge_commit_sha"]

    ref = event.data["pull_request"]["base"]["ref"]

    await _notify(github_api, ref,
                  repository_name=repository_name,
                  user=user,
                  url=url,
                  action=action,
                  pull_id=pull_id,
                  title=title)


@github.register("issue_comment")
async def issue_comment(event, github_api):
    if "pull_request" not in event.data["issue"]:
        return

    if event.data["action"] != "created":
        return

    repository_name = event.data["repository"]["full_name"]
    pull_id = event.data["issue"]["number"]
    url = event.data["comment"]["html_url"]
    user = event.data["sender"]["login"]

    # To not assume Pull Request are always against 'master',
    # we take an extra roundtrip to find the base branch
    pull_request_url = event.data["issue"]["pull_request"]["url"]
    assert pull_request_url.startswith("https://api.github.com")
    pull_request_url = pull_request_url[len("https://api.github.com"):]
    response = await github_api.getitem(pull_request_url)
    ref = response["base"]["ref"]
    title = response["title"]

    await _notify(github_api, ref,
                  repository_name=repository_name,
                  user=user,
                  url=url,
                  action="comment",
                  pull_id=pull_id,
                  title=title)
