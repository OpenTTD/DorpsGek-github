from dorpsgek_github.core.yaml.exceptions import YAMLDuplicatedKeyword

_keywords = {}


def register(keyword):
    """Register a keyword to make it available in the YAML configuiration."""

    if keyword in _keywords:
        raise YAMLDuplicatedKeyword(keyword)

    def wrapped(func):
        _keywords[keyword] = func
        return func
    return wrapped


def get_keyword_handler(keyword):
    """Get the handler for a given keyword."""
    return _keywords[keyword]
