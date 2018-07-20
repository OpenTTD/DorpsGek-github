from dorpsgek_github.core.processes.runner import RunnerContext
from dorpsgek_github.core.yaml.keywords import dorpsgek


@dorpsgek.register("build")
async def build(job, context):
    """
    Create a container which can be deployed.

    This requires a valid Dockerfile in the root of the repository.
    """

    async with RunnerContext(environment=job.environment) as runner_ws:
        artifact_name = "source"
        source_filename = f"{context.artifact_folder}/{artifact_name}.tar.gz"

        await runner_ws.send_request("job.start")
        await runner_ws.send_artifact(artifact_name, source_filename)
        await runner_ws.send_request("docker.build", {
            "name": context.repository_name,
            "tag": context.ref,
        })
        await runner_ws.send_request("docker.push", {
            "name": context.repository_name,
            "tag": context.ref,
        })
        await runner_ws.send_request("job.done")
