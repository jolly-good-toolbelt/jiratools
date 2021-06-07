"""Search command."""
from typing import Optional

from .utils import get_client


def cli_search(query, max_results: Optional[int], count_only: bool) -> None:
    """Search using JQL and return matches."""
    client = get_client()

    results = client.search_issues(
        query, maxResults=False if count_only else max_results
    )

    print('Search for "{}" returned {} results'.format(query, len(results)))
    if count_only:
        return
    for issue in results:
        print("{}: {}".format(issue.permalink(), issue.fields.summary))
