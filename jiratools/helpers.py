"""A collection of helpers for JIRA commands."""
from typing import List

import jira
from jgt_common import exit, error_if
import requests

from .utils import DEFAULT_LINK_TYPE
from .utils import get_client, load_config


def find_jira_helper(jira_id: str) -> jira.resources.Issue:
    """
    Find the JIRA of a given id, or exit if not found.

    Args:
        jira_id: the id of the desired JIRA

    Returns:
        the issue with the provided id

    """
    client = get_client()
    try:
        dev_jira = client.issue(jira_id)
    except jira.exceptions.JIRAError:
        print("JIRA {} was not found!".format(jira_id))
        exit(1)
    return dev_jira


def list_from_config(key_name: str) -> List[str]:
    """
    Return a list from a comma-separated config file entry.

    Args:
        key_name: the name of the key in the config

    Returns:
        a list of string values

    """
    config = load_config()
    return list(filter(None, [x.strip() for x in config.get(key_name, "").split(",")]))


def component_id_from_name(
    project_components: List[jira.resources.Component], component_name: str
) -> str:
    """
    Retrive the id of the compoment with the desired name.

    Args:
        project_components: a list of all components associated with a JIRA project
        component_name: the name of the desired component

    Returns:
        the id of the matching component

    """
    matches = [x.id for x in project_components if x.name == component_name]
    message = "More than one component in project with name: {}"
    error_if(len(matches) != 1, message=message.format(component_name))
    return matches[0]


def link_jiras(
    client: jira.JIRA,
    from_jira: str,
    to_jira: str,
    relation_type: str = DEFAULT_LINK_TYPE,
) -> requests.Response:
    """
    Create a link between two JIRA issues.

    Args:
        client: the instantiated JIRA client
        from_jira: a JIRA issue id
        to_jira: a JIRA issue id
        relation_type: the type of link relationship

    Returns:
        the client Response

    """
    return client.create_issue_link(relation_type, from_jira, to_jira)


def add_comment(jira_id: str, comment_text: str) -> jira.resources.Comment:
    """
    Add a comment to the JIRA ID.

    Args:
        jira_id: The JIRA ID to comment on.
        comment_text: The text to add as the comment body.

    Returns:
        A jira comment.

    """
    return get_client().add_comment(jira_id, comment_text)


def check_for_valid_user(user: str) -> None:
    """
    Ensure that a user exists, exit if not found.

    Args:
        user: the user id

    """
    client = get_client()
    try:
        user = client.user(user)
    except jira.exceptions.JIRAError as e:
        print("There was a problem finding user {}. Error message: {}.".format(user, e))
        exit(1)
