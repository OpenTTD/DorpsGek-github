from dorpsgek_github.core.helpers.github import get_dorpsgek_yml
from dorpsgek_github.core.processes.github import router as github
from dorpsgek_github.core.scheduler.scheduler import schedule_task
from dorpsgek_github.core.yaml.loader import load_yaml


@github.register("push")
async def push(event, github_api):
    branch = event.data["ref"]
    ref = event.data["head_commit"]["id"]
    repository_name = event.data["repository"]["full_name"]
    clone_url = event.data["repository"]["clone_url"]

    assert branch.startswith("refs/heads/")
    branch = branch[len("refs/heads/"):]

    # Get the .dorpsgek.yml, so we know what to do
    raw_yml = await get_dorpsgek_yml(github_api, repository_name, ref)
    config = load_yaml(raw_yml)

    # Figure out which jobs need to be executed
    jobs_to_execute = []
    for stage, jobs in config.items():
        for job in jobs:
            if not job.match(branch=branch):
                continue
            if job.manual:
                continue

            jobs_to_execute.append(job)

    # Schedule this task for execution
    await schedule_task(jobs_to_execute, repository_name, ref, clone_url)
