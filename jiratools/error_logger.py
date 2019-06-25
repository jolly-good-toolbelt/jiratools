"""Error logging for jiratools."""
from typing import List, Iterable

from jiratools import add_comment, format_as_code_block
from jiratools.formatting import (
    DataArray,
    format_autoupdate_jira_msg,
    format_as_jira_table,
)

DataHeaders = List[str]


class JiraEntry:
    """Typing mock for Jira Entry data."""

    jira_id: str
    error_message: str


def add_jira_error_comment(jira_id: str, error_msg: str, **format_kwargs) -> str:
    """
    Add a comment to a JIRA with a formatted error message.

    Args:
        jira_id: the Issue ID of the JIRA to be updated
        error_msg: the raw error message to include in the comment
        **format_kwargs: formatting keyword args
            to be passed to jiratools.formatting.format_jira_msg

    Returns:
        the Issue ID of the JIRA which received the comment

    """
    add_comment(
        jira_id,
        format_autoupdate_jira_msg(format_as_code_block(error_msg), **format_kwargs),
    )
    return jira_id


def add_jira_comment_with_table(
    jira_id: str,
    data_headers: DataHeaders,
    data_array: DataArray,
    msg_prefix: str = "",
    **format_kwargs
) -> str:
    """
    Add a comment to a JIRA with a formatted data table.

    Args:
        jira_id: the Issue ID of the JIRA to be updated
        data_headers: a list of header column names
        data_array: An array of lists of strings,
            representing table rows. e.g.::

            [["a", "b", "c"], ["d", "e", "f"]]

        **format_kwargs: formatting keyword args
            to be passed to jiratools.formatting.format_jira_msg

    Returns:
        str: the Issue ID of the JIRA which received the comment

    """
    message_with_table = "{}{}".format(
        msg_prefix, format_as_jira_table(data_headers, data_array)
    )
    add_comment(
        jira_id, format_autoupdate_jira_msg(message_with_table, **format_kwargs)
    )
    return jira_id


def update_jira_for_errors(
    jiras: Iterable[JiraEntry], *errors: str, **format_kwargs
) -> List[str]:
    """
    Auto-Update JIRAs if errors are found that match the jira list.

    Args:
        jiras: an iterable of objects
            that each contain two required attributes

            - jira_id: the Issue Id of the JIRA to be updated
            - error_message: an error message substring which, if found,
              will trigger and update of the JIRA with the actual error message.

        *errors: an error message to be checked against the ``jiras`` for a match
        **format_kwargs: formatting keyword args
            to be passed to jiratools.formatting.format_jira_msg

    Returns:
        A list of JIRA Issue IDs that were updated.

    """
    jiras_commented = []
    for jira in jiras:
        for error in errors:
            if jira.error_message and jira.error_message in error:
                jiras_commented.append(
                    add_jira_error_comment(jira.jira_id, error, **format_kwargs)
                )
    return jiras_commented
