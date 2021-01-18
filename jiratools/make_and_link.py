"""Make a linked story command."""
from typing import List

from .utils import get_client
from .helpers import get_issue_by_id, component_id_from_name, link_jiras


def cli_make_linked(
    jira_id: str,
    project: str,
    summary: str,
    description: str,
    issue_type: str,
    user: str,
    assign: bool,
    labels: List[str],
    components: List[str],
    watchers: str,
) -> None:
    """Build a new story linked to the given one."""
    client = get_client()
    dev_jira = get_issue_by_id(jira_id)
    issue_data = {
        "project": project,
        "summary": summary.format(
            dev_jira_id=dev_jira.key, dev_jira_summary=dev_jira.fields.summary
        ),
        "description": description,
        "issuetype": {"name": issue_type},
    }
    if assign:
        issue_data.update(assignee={"name": user or client.current_user()})
    if labels:
        issue_data.update(labels=labels)
    if components:
        project_components = client.project_components(project)
        issue_data.update(
            components=[
                {"id": component_id_from_name(project_components, x)}
                for x in components
            ]
        )
    test_jira = client.create_issue(**issue_data)
    link_jiras(test_jira.key, dev_jira.key, client=client)
    for to_watch in watchers:
        client.add_watcher(test_jira.key, to_watch)
    print("Test JIRA Created: {}".format(test_jira.permalink()))
