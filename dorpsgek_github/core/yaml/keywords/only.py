from dorpsgek_github.core.yaml import registry as yaml


@yaml.register("only")
def only(job, data):
    """
    Restrict when this job can execute.

    This can either be one of these values:
     - 'branches': only execute when something is pushed to a branch (any branch)
     - 'tags': only execute when something is pushed to a branch (any tag)

    Or it can be a value which matches the branch name or tag name, e.g.: master

    This can be a list, which is OR'd. So if any of the values match, the job is executed.
    """

    if not isinstance(data, list):
        data = [data]

    for include in data:
        if include == "branches":
            job.add_include(lambda branch, tag: branch)
        elif include == "tags":
            job.add_include(lambda branch, tag: tag)
        else:
            # TODO -- Support regex
            job.add_include(lambda branch, tag: include == branch or include == tag)
