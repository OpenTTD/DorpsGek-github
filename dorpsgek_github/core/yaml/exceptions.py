class YAMLConfigurationError(Exception):
    """There is a configuration error."""


class YAMLConfigurationErrors(Exception):
    """All configuration errors in a list during configuration parsing."""


class YAMLDuplicatedKeyword(Exception):
    """Thrown if the same keyword is registered twice."""


class YAMLDuplicatedDorpsgekCommand(Exception):
    """Thrown if the same DorpsGek command is registered twice."""
