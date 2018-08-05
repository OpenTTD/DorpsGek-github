import os

from collections import defaultdict

from dorpsgek_github import config


class ConfigurationEmpty(Exception):
    """Thrown if the configuration entry remained empty."""


def post_load_config():
    if not os.path.exists(config.REFERENCE_REPOSITORY_FOLDER):
        os.makedirs(config.REFERENCE_REPOSITORY_FOLDER, exist_ok=True)
    if not os.path.exists(config.WORKING_FOLDER):
        os.makedirs(config.WORKING_FOLDER, exist_ok=True)

    with open(config.GITHUB_APP_PRIVATE_KEY_FILE) as f:
        setattr(config, "GITHUB_APP_PRIVATE_KEY", f.read())

    notification_dict = defaultdict(list)
    for notification in config.NOTIFICATIONS.split(" "):
        protocol, _, userdata = notification.partition(".")
        notification_dict[protocol].append(userdata)
    setattr(config, "NOTIFICATIONS_DICT", notification_dict)


def load_config():
    for key in dir(config):
        # Only accept config entries that start with a capital
        if key[0] < "A" or key[0] > "Z":
            continue

        value = getattr(config, key)

        if key in os.environ:
            value = os.environ[key]

        if isinstance(value, list):
            value = " ".join(value)

        setattr(config, key, value)

    post_load_config()

    for key in dir(config):
        # Only accept config entries that start with a capital
        if key[0] < "A" or key[0] > "Z":
            continue

        if getattr(config, key) is None:
            raise ConfigurationEmpty(key)
