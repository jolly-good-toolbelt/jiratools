"""Make a linked story command."""
import argparse

from .utils import get_client
from .helpers import get_issue_by_id, component_id_from_name, link_jiras


def cli_make_linked(args: argparse.Namespace) -> None:
    """Build a new story linked to the given one."""
    client = get_client()
    dev_jira = get_issue_by_id(args.jira_id)
    issue_data = {
        "project": args.project,
        "summary": args.summary.format(
            dev_jira_id=dev_jira.key, dev_jira_summary=dev_jira.fields.summary
        ),
        "description": args.description,
        "issuetype": {"name": args.issue_type},
    }
    if args.assign:
        issue_data.update(assignee={"name": args.user or client.current_user()})
    if args.labels:
        issue_data.update(labels=args.labels)
    if args.components:
        project_components = client.project_components(args.project)
        issue_data.update(
            components=[
                {"id": component_id_from_name(project_components, x)}
                for x in args.components
            ]
        )
    test_jira = client.create_issue(**issue_data)
    link_jiras(test_jira.key, dev_jira.key, client=client)
    for to_watch in args.watchers:
        client.add_watcher(test_jira.key, to_watch)
    print("Test JIRA Created: {}".format(test_jira.permalink()))
