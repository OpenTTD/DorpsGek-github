import base64
import gidgethub
import os

from dorpsgek_github import config
from dorpsgek_github.core.helpers.subprocess import run_command


async def download_repository(repository, ref, clone_url, work_folder):
    """Download a GitHub repository, and compress it into a tarball."""

    reference_folder = f"{config.REFERENCE_REPOSITORY_FOLDER}/{repository}"
    repository_folder = f"{work_folder}/source"
    repository_tarball = f"{work_folder}/artifact/source.tar.gz"

    if not os.path.exists(reference_folder):
        await run_command(f"git clone --mirror {clone_url} {reference_folder}")
    else:
        await run_command(f"git fetch --all", cwd=reference_folder)

    await run_command(f"git clone --reference {reference_folder} {clone_url} {repository_folder}")
    await run_command(f"git checkout {ref}", cwd=repository_folder)
    await run_command(f"tar zcf {repository_tarball} .", cwd=repository_folder)


async def get_dorpsgek_yml(github_api, repository, ref):
    """Get the .dorpsgek.yml from a repository."""
    try:
        response = await github_api.getitem(f"/repos/{repository}/contents/.dorpsgek.yml?ref={ref}")
    except gidgethub.BadRequest as err:
        if err.args != ("Not Found",):
            raise

        # No .dorpsgek.yml in this repository; so nothing to do!
        return

    return base64.b64decode(response["content"])
