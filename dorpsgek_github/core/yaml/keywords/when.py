from dorpsgek_github.core.yaml import registry as yaml
from dorpsgek_github.core.yaml.exceptions import YAMLConfigurationError

OPTIONS = ["manual"]


@yaml.register("when")
def when(job, data):
    """
    When this job should execute.

    Currnetly only 'manual' is valid, meaning the job needs a manual trigger before running.
    """

    if data not in OPTIONS:
        supported_options = ",".join(OPTIONS)
        raise YAMLConfigurationError(f"'when' has value '{data}'; supported: {supported_options}")

    job.set_manual()
