"""Issue Reassignment command."""
import argparse

import jira

from .utils import get_client
from .helpers import check_for_valid_user, get_issue_by_id


def cli_reassign(args: argparse.Namespace) -> None:
    """Change issue assignment."""
    client = get_client()
    get_issue_by_id(args.jira_id)
    check_for_valid_user(args.user)
    try:
        client.assign_issue(args.jira_id, args.user)
    except jira.exceptions.JIRAError as e:
        print('ERROR: "{}" trying to assign a new user to the JIRA.'.format(e.text))
