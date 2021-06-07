"""Basic utility functions for JIRA tools."""
from configparser import ConfigParser, SectionProxy
import os
from pathlib import Path

import jira
from jgt_common import error_if

CONFIG_FILENAME = str(Path.home() / "jira.config")
CONFIG = None

SAMPLE_CONFIG_FILENAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "jira.config.example"
)

REQUIRED_KEYS = ("JIRA_URL", "USERNAME", "PASSWORD", "DEFAULT_ASSIGNEE", "TEST_PROJECT")
DEFAULT_LINK_TYPE = "relates to"


class ConfigNotFoundException(Exception):
    """Exception for config failure."""

    pass


def get_client() -> jira.JIRA:
    """
    Return a configured JIRA client.

    Configured per the user's home directory ``jira.config`` file.

    """
    load_config()
    if not CONFIG:
        raise ConfigNotFoundException
    client = jira.JIRA(
        CONFIG["JIRA_URL"],
        basic_auth=(CONFIG["USERNAME"], CONFIG.get("PASSWORD", raw=True)),
    )
    return client


def load_config() -> SectionProxy:
    """
    Load CONFIG_FILENAME into CONFIG.

    If not already loaded; call before touching CONFIG

    """
    global CONFIG
    if CONFIG is not None:
        return CONFIG

    config = ConfigParser()
    message = 'Config file "{}" {{}}'.format(CONFIG_FILENAME)
    error_if(not Path(CONFIG_FILENAME).exists(), message=message.format("not found"))
    config.read(CONFIG_FILENAME)
    section_name = "jira"
    error_if(
        section_name not in config,
        message=message.format('missing "{}" section'.format(section_name)),
    )
    missing_keys = [key for key in REQUIRED_KEYS if key not in config[section_name]]
    missing_message = message.format(
        'section "{}" missing keys: {{}}'.format(section_name)
    )
    error_if(missing_keys, message=missing_message)
    CONFIG = config[section_name]
    return CONFIG
