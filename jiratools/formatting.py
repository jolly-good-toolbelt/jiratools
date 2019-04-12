import getpass
import os


def _build_source():
    return os.environ.get("BUILD_URL", f"Manual run by {getpass.getuser()}")


def format_autoupdate_jira_msg(message_body, header_body=None):
    """
    Format a JIRA message with useful headers.


    An "Automated JIRA Update" title will be added,
    as well as either a URL link if a ``BUILD_URL`` env variable is present,
    or a note indicating a manual run with user id otherwise.

    Args:
        message_body (str): the body of the message
        header_body (str, optional): a header to be added with ``h2`` tag

    Returns:
        str: a formatted message with headers
    """
    message = "h2. {}".format(header_body) if header_body else ""
    message += "\n\nAutomated JIRA Update:\n\n{}\n\n{}".format(
        _build_source(), message_body
    )
    return message


def format_as_jira_table(headers, data_array):
    """
    Build a JIRA table given headers and row data.

    Args:
        headers (list of str): a list of header column names
        data_array (list of list of str,int): An array of lists of strings,
            representing table rows. e.g.::

            [["a", "b", "c"], ["d", "e", "f"]]

    Returns:
        str: a formatted JIRA table
    """
    headers = ["||{}||".format("||".join(headers))]
    return "\n".join(
        headers + ["|{}|".format("|".join(map(str, d))) for d in data_array]
    )
