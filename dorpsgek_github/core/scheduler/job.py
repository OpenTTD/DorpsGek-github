DEFAULT_ENVIRONMENT = "testing"


class Job:
    """Collected configuration for a job."""

    def __init__(self, name):
        self.name = name
        self.manual = False
        self.environment = DEFAULT_ENVIRONMENT
        self.executor = None

        self._include_filter = []

    def add_include(self, func):
        self._include_filter.append(func)

    def set_manual(self):
        self.manual = True

    def set_environment(self, environment):
        self.environment = environment

    def set_executor(self, func):
        self.executor = func

    def is_valid(self):
        return self.environment and self.executor

    def match(self, *, branch=None, tag=None):
        if not self._include_filter:
            return True

        for func in self._include_filter:
            if func(branch=branch, tag=tag):
                return True

        return False
