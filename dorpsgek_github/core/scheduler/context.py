class Context:
    """Context information for a job."""

    def __init__(self, *, repository_name, ref, artifact_folder):
        self.repository_name = repository_name
        self.ref = ref
        self.artifact_folder = artifact_folder
