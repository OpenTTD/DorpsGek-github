from dorpsgek_github.core.yaml.exceptions import (
    YAMLConfigurationError,
    YAMLDuplicatedDorpsgekCommand,
)
from dorpsgek_github.core.yaml import registry as yaml

_registry = {}


@yaml.register("dorpsgek")
def dorpsgek(job, data):
    """Order DorpsGek to execute certain commands."""

    if data not in _registry.keys():
        supported_keys = ",".join(_registry.keys())
        raise YAMLConfigurationError(f"'dorpsgek' has value '{data}'; supported: {supported_keys}")

    job.set_executor(_registry[data])


def register(command):
    """
    Register a single DorpsGek command.

    This will become the executor for the command, and should be a coroutine.
    """

    if command in _registry:
        raise YAMLDuplicatedDorpsgekCommand(command)

    def wrapper(func):
        _registry[command] = func
        return func
    return wrapper
