import asyncio
import importlib
import logging

from aiohttp import web

from dorpsgek_github import config
from dorpsgek_github.core.helpers.aiohttp_web import (
    prepare_app,
    run_apps,
)
from dorpsgek_github.core.aiohttp_apps.github import (
    github_handler,
    github_probe_handler,
    github_startup,
)
from dorpsgek_github.core.aiohttp_apps.runner import runner_handler
from dorpsgek_github.core.load_config import load_config
from dorpsgek_github.core.scheduler.scheduler import schedule_runner

log = logging.getLogger(__name__)
MODULES_ALWAYS_LOAD = ["ping", "registration"]
KEYWORDS_ALWAYS_LOAD = ["dorpsgek", "environment", "only", "when"]


def create_web_apps():
    apps = []

    github_app = web.Application()
    github_app.router.add_get("/probe", github_probe_handler)
    github_app.router.add_post("/", github_handler)
    github_app.on_startup.append(github_startup)
    apps.append(prepare_app(github_app, port=config.GITHUB_APP_PORT))

    runner_app = web.Application()
    runner_app.router.add_get("/", runner_handler)
    apps.append(prepare_app(runner_app, port=config.RUNNER_PORT))

    return apps


def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)
    load_config()

    for module in config.MODULES.split() + MODULES_ALWAYS_LOAD:
        importlib.import_module(f"dorpsgek_github.modules.{module}")

    for keyword in KEYWORDS_ALWAYS_LOAD:
        importlib.import_module(f"dorpsgek_github.core.yaml.keywords.{keyword}")

    for commands in config.DORPSGEK_COMMANDS.split():
        importlib.import_module(f"dorpsgek_github.dorpsgek_commands.{commands}")

    apps = create_web_apps()

    asyncio.ensure_future(schedule_runner())
    run_apps(apps, print=log.info)


if __name__ == "__main__":
    main()
