"""Link JIRAs command."""
import argparse

import jira

from .utils import get_client
from .helpers import link_jiras


def cli_jira_link(args: argparse.Namespace) -> None:
    """Create JIRA link."""
    print(
        'Creating a "{}" link from "{}" to "{}"'.format(
            args.link_type, args.from_jira, args.to_jira
        )
    )
    try:
        client = get_client()
        link_jiras(client, args.from_jira, args.to_jira, args.link_type)
    except jira.exceptions.JIRAError as e:
        print('ERROR: "{}" trying to make the link.'.format(e.text))
