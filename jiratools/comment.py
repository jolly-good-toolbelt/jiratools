"""Add Comment command."""
import sys

import jira

from .helpers import add_comment


def cli_add_comment(jira_id: str, message: str) -> jira.resources.Comment:
    """Add comment to issue."""
    if message == "-":
        message = sys.stdin.read()
        # Add a blank line for spacing.
        print()

    print('Adding comment "{}" to "{}"'.format(message, jira_id))
    try:
        add_comment(jira_id, message)
    except jira.exceptions.JIRAError as e:
        print('ERROR: "{}" for "{}"!'.format(e.text, jira_id))
