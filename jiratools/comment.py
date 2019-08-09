"""Add Comment command."""
import argparse
import sys

import jira

from .helpers import add_comment as add_comment


def cli_add_comment(args: argparse.Namespace) -> jira.resources.Comment:
    """Add comment to issue."""
    if args.message == "-":
        args.message = sys.stdin.read()
        print()

    print('Adding comment "{}" to "{}"'.format(args.message, args.jira_id))
    try:
        add_comment(args.jira_id, args.message)
    except jira.exceptions.JIRAError as e:
        print('ERROR: "{}" for "{}"!'.format(e.text, args.jira_id))
