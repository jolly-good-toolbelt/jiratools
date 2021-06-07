"""Link JIRAs command."""

import jira

from .helpers import link_jiras


def cli_jira_link(link_type: str, from_jira: str, to_jira: str) -> None:
    """Create JIRA link."""
    print(
        'Creating a "{}" link from "{}" to "{}"'.format(link_type, from_jira, to_jira)
    )
    try:
        link_jiras(from_jira, to_jira, link_type)
    except jira.exceptions.JIRAError as e:
        print('ERROR: "{}" trying to make the link.'.format(e.text))
