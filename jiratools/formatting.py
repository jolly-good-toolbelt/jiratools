"""Formatting helpers for jiratools."""
import getpass
import os
from typing import Optional, List, Union

TableRowData = List[Union[str, int]]
DataArray = List[TableRowData]


def _build_source() -> str:
    return os.environ.get("BUILD_URL", "Manual run by {}".format(getpass.getuser()))


def format_autoupdate_jira_msg(
    message_body: str, header_body: Optional[str] = None
) -> str:
    """
    Format a JIRA message with useful headers.

    An "Automated JIRA Update" title will be added,
    as well as either a URL link if a ``BUILD_URL`` env variable is present,
    or a note indicating a manual run with user id otherwise.

    Args:
        message_body: the body of the message
        header_body: a header to be added with ``h2`` tag

    Returns:
        a formatted message with headers

    """
    message = "h2. {}".format(header_body) if header_body else ""
    message += "\n\nAutomated JIRA Update:\n\n{}\n\n{}".format(
        _build_source(), message_body
    )
    return message


def format_as_jira_table(headers: List[str], data_array: DataArray) -> str:
    """
    Build a JIRA table given headers and row data.

    Args:
        headers: a list of header column names
        data_array: An array of lists, representing table rows. e.g.::

            [["a", "b", "c"], ["d", "e", "f"]]

    Returns:
        a formatted JIRA table

    """
    headers = ["||{}||".format("||".join(headers))]
    return "\n".join(
        headers + ["|{}|".format("|".join(map(str, d))) for d in data_array]
    )
