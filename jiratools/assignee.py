"""Issue Reassignment command."""
import jira

from .utils import get_client
from .helpers import check_for_valid_user, get_issue_by_id


def cli_reassign(jira_id: str, user: str) -> None:
    """Change issue assignment."""
    client = get_client()
    get_issue_by_id(jira_id)
    check_for_valid_user(user)
    try:
        client.assign_issue(jira_id, user)
    except jira.exceptions.JIRAError as e:
        print(
            'ERROR: "{}" trying to assign a new user to the JIRA "{}".'.format(
                e.text, jira_id
            )
        )
