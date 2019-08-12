"""Search command."""
import argparse

from .utils import get_client


def cli_search(args: argparse.Namespace) -> None:
    """Search using JQL and return matches."""
    client = get_client()

    results = client.search_issues(
        args.query, maxResults=False if args.count_only else args.max_results
    )

    print('Search for "{}" returned {} results'.format(args.query, len(results)))
    if args.count_only:
        return
    for issue in results:
        print("{}: {}".format(issue.permalink(), issue.fields.summary))
