import asyncio
import logging
import os
import tempfile

from dorpsgek_github import config
from dorpsgek_github.core.helpers.github import download_repository
from dorpsgek_github.core.processes.runner import (
    NoRunnerException,
    RunnerIsGone,
)
from dorpsgek_github.core.scheduler.context import Context

log = logging.getLogger(__name__)
task_list = asyncio.Queue()


async def schedule_task(jobs_to_execute, repository_name, ref, clone_url):
    task_coroutine = execute_task(jobs_to_execute, repository_name, ref, clone_url)
    log.info("Scheduling new task; %d in queue now", task_list.qsize() + 1)
    task_list.put_nowait(task_coroutine)


async def schedule_runner():
    """Simple implementation for a scheduler.

    It picks up the first task to do, starts the task, wait till it finishes,
    and picks up the next.
    """
    while True:
        task_coroutine = await task_list.get()
        log.info("Scheduler picking up new task; %d left in queue", task_list.qsize())
        try:
            await task_coroutine
        except Exception:
            log.exception("Unexpected error while executing a task")


async def execute_task(jobs_to_execute, repository_name, ref, clone_url):
    """
    Execute a full task.

    This creates a temporary directory, fetches the source code (and makes that an artifact), and runs all the jobs.
    """
    repository_name_safe = repository_name.replace("/", "-")
    prefix = f"dorpsgek.{repository_name_safe}."
    with tempfile.TemporaryDirectory("", prefix, config.WORKING_FOLDER) as work_folder:
        artifact_folder = f"{work_folder}/artifact"

        os.mkdir(artifact_folder)
        await download_repository(repository_name, ref, clone_url, work_folder)

        context = Context(repository_name=repository_name, ref=ref, artifact_folder=artifact_folder)

        for job in jobs_to_execute:
            try:
                await job.executor(job, context)
            except RunnerIsGone:
                log.error("The runner for this job is no longer available; aborting task!")
                break
            except NoRunnerException as err:
                log.error("No runner registered for environment '%s'; cannot schedule job. Aborting task!",
                          err.args[0])
                break
