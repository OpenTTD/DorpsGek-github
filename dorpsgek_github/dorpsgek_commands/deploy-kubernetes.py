from dorpsgek_github.core.processes.runner import RunnerContext
from dorpsgek_github.core.yaml.keywords import dorpsgek


@dorpsgek.register("deploy")
async def deploy(job, context):
    """Deploy a container to an environment."""

    async with RunnerContext(environment=job.environment) as runner_ws:
        await runner_ws.send_request("job.start")
        await runner_ws.send_request("kubernetes.deploy", {
            "name": context.repository_name,
            "tag": context.ref,
        })
        await runner_ws.send_request("job.done")
