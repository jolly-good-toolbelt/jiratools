"""Some simple API functions and command-line tools for interaction with JIRA."""

from __future__ import print_function
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
    RawDescriptionHelpFormatter,
)
from configparser import ConfigParser
import os
import shutil
import sys

import jira


REQUIRED_KEYS = ("JIRA_URL", "USERNAME", "PASSWORD", "DEFAULT_ASSIGNEE", "TEST_PROJECT")
DEFAULT_LINK_TYPE = "relates to"

CONFIG_FILENAME = os.path.join(os.path.expanduser("~"), "jira.config")
SAMPLE_CONFIG_FILENAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "jira.config.example"
)
CONFIG = None


def exit(status=0, message=None):
    """
    Exit the program and optionally print a message to standard error.

    Args:
        status (int): Exit code to use for exit (optional)
        message (string): Message to print to standard error (optional)
    """
    if message:
        print(message, file=sys.stderr)
    sys.exit(status)


def error_if(check, status=None, message=""):
    """
    Exit the program if a provided check is true.

    Exit the program if the check is true.
    If a status is provided,
    that code is used for the exit code;
    otherwise the value from the check is used.
    An optional message for standard error can also be provided.

    Args:
        check: Anything with truthiness that can determine
            if the program should exit or not
        status (int): Exit code to use for exit (optional)
        message (string): Message to print to standard error if check is True (optional)
    """
    if check:
        exit(status=status or check, message=message.format(check))


def _load_config():
    """
    Load CONFIG_FILENAME into CONFIG.

    If not already loaded; call before touching CONFIG

    """
    global CONFIG
    if CONFIG is not None:
        return

    config = ConfigParser()
    message = 'Config file "{}" {{}}'.format(CONFIG_FILENAME)
    error_if(not os.path.exists(CONFIG_FILENAME), message=message.format("not found"))
    config.read(CONFIG_FILENAME)
    section_name = "jira"
    error_if(
        section_name not in config,
        message=message.format('missing "{}" section'.format(section_name)),
    )
    missing_keys = [key for key in REQUIRED_KEYS if key not in config[section_name]]
    missing_message = message.format(
        'section "{}" missing keys: {{}}'.format(section_name)
    )
    error_if(missing_keys, status=1, message=missing_message)
    CONFIG = config[section_name]


def get_client():
    """
    Returns a configured JIRA client.

    Configured per the user's home directory ``jira.config`` file.

    """
    _load_config()
    client = jira.JIRA(
        CONFIG["JIRA_URL"],
        basic_auth=(CONFIG["USERNAME"], CONFIG.get("PASSWORD", raw=True)),
    )
    return client


def format_as_code_block(text_to_wrap):
    """
    Wrap the text in a JIRA code block.

    Args:
        text_to_wrap (str): The text to wrap.

    Returns:
        str: A JIRA formatted code block.
    """
    return "".join(["{code:java}", "{}".format(text_to_wrap), "{code}"])


def add_comment(jira_id, comment_text):
    """
    Add a comment to the JIRA ID.

    Args:
        jira_id (str): The JIRA ID to comment on.
        comment_text (str): The text to add as the comment body.

    Returns:
        A jira comment.
    """
    return get_client().add_comment(jira_id, comment_text)


def _link_jiras(client, from_jira, to_jira, relation_type=DEFAULT_LINK_TYPE):
    return client.create_issue_link(relation_type, from_jira, to_jira)


def cli_jira_link():
    """
    Link two JIRAs as related.

    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("from_jira", help="The JIRA from which to create the link.")
    parser.add_argument("to_jira", help="The JIRA to which to create the link.")
    parser.add_argument(
        "-t",
        "--link-type",
        help="The type of link to create.",
        default=DEFAULT_LINK_TYPE,
    )
    args = parser.parse_args()
    print(
        'Creating a "{}" link from "{}" to "{}"'.format(
            args.link_type, args.from_jira, args.to_jira
        )
    )
    try:
        client = get_client()
        _link_jiras(client, args.from_jira, args.to_jira, args.link_type)
    except jira.exceptions.JIRAError as e:
        print('ERROR: "{}" trying to make the link.'.format(e.text))


def _list_from_config(key_name):
    _load_config()
    return list(filter(None, [x.strip() for x in CONFIG.get(key_name, "").split(",")]))


def _component_id_from_name(project_components, component_name):
    matches = [x.id for x in project_components if x.name == component_name]
    message = "More than one component in project with name: {}"
    error_if(len(matches) != 1, message=message.format(component_name))
    return matches[0]


def _test_story_args():
    _load_config()
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("jira_id")
    parser.set_defaults(assign=bool(CONFIG["DEFAULT_ASSIGNEE"]))
    assignment = parser.add_mutually_exclusive_group()
    assignment.add_argument(
        "--assign",
        dest="assign",
        action="store_true",
        help="Assign story to user, current user if none provided.",
    )
    assignment.add_argument(
        "--no-assign",
        dest="assign",
        action="store_false",
        help="Leave Test JIRA unassigned",
    )
    parser.add_argument(
        "-p",
        "--project",
        default=CONFIG["TEST_PROJECT"],
        help="JIRA project in which to create test story",
    )
    parser.add_argument(
        "-u",
        "--user",
        default=CONFIG["DEFAULT_ASSIGNEE"],
        help="the user who will receive the assignment",
    )
    parser.add_argument(
        "-c",
        "--components",
        default=_list_from_config("DEFAULT_COMPONENTS"),
        action="append",
        help="Component tag to be aplied to the Test Story",
    )
    parser.add_argument(
        "-d",
        "--description",
        default=CONFIG["DEFAULT_DESCRIPTION"],
        help="Description string for Test JIRA.",
    )
    parser.add_argument(
        "-l",
        "--labels",
        default=_list_from_config("DEFAULT_LABELS"),
        action="append",
        help="Comma-separated list of labels to be applied to the Test story",
    )
    parser.add_argument(
        "-s",
        "--summary",
        default=CONFIG["DEFAULT_SUMMARY"],
        help="Summary string for Test JIRA - will receive the Dev JIRA key and "
        "summary as string format values",
    )
    parser.add_argument(
        "-t",
        "--issue-type",
        default=CONFIG["DEFAULT_ISSUE_TYPE"],
        help="Issue type for Test JIRA -- "
        "must be a valid type name on target project",
    )
    parser.add_argument(
        "-w",
        "--watchers",
        action="append",
        default=_list_from_config("WATCHERS"),
        help="Watchers to add to Test JIRA",
    )
    args = parser.parse_args()
    return args


def _cli_add_comment():
    """
    Quick "add a short comment to a JIRA" command line tool.

    If 'message' is '-' then stdin will be read.
    """
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=_cli_add_comment.__doc__,
    )
    parser.add_argument("jira_id")
    parser.add_argument("message", help="Comment to add to the given JIRA.")
    args = parser.parse_args()

    if args.message == "-":
        args.message = sys.stdin.read()
        print()

    print('Adding comment "{}" to "{}"'.format(args.message, args.jira_id))
    try:
        add_comment(args.jira_id, args.message)
    except jira.exceptions.JIRAError as e:
        print('ERROR: "{}" for "{}"!'.format(e.text, args.jira_id))


def _cli_search():
    """
    Search using JQL and return matches.
    """
    client = get_client()
    default_max_count = int(CONFIG.get("MAX_RESULT_COUNT", 0)) or 10
    default_max_count = False if default_max_count == -1 else default_max_count
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    result_count = parser.add_mutually_exclusive_group()
    result_count.add_argument(
        "--max-results",
        "-m",
        type=int,
        default=default_max_count,
        help="Max results returned.",
    )
    result_count.add_argument(
        "--no-max-count", "-n", action="store_false", dest="max_results"
    )
    parser.add_argument("--count-only", "-c", action="store_true")
    parser.add_argument("query")
    args = parser.parse_args()

    results = client.search_issues(
        args.query, maxResults=False if args.count_only else args.max_results
    )

    print('Search for "{}" returned {} results'.format(args.query, len(results)))
    if args.count_only:
        return
    for issue in results:
        print("{}: {}".format(issue.permalink(), issue.fields.summary))


def _create_test_jira_from():
    args = _test_story_args()
    client = get_client()
    try:
        dev_jira = client.issue(args.jira_id)
    except jira.exceptions.JIRAError:
        print("JIRA {} was not found!".format(args.jira_id))
        exit(1)
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
                {"id": _component_id_from_name(project_components, x)}
                for x in args.components
            ]
        )
    test_jira = client.create_issue(**issue_data)
    _link_jiras(client, test_jira.key, dev_jira.key)
    for to_watch in args.watchers:
        client.add_watcher(test_jira.key, to_watch)
    print("Test JIRA Created: {}".format(test_jira.permalink()))


def _example_config_install():
    error_if(
        not os.path.exists(SAMPLE_CONFIG_FILENAME),
        message="Missing example config file: {}".format(SAMPLE_CONFIG_FILENAME),
    )

    parser = ArgumentParser(
        description="Install example jira.config in your homne directory "
        "unless you have one already. Without any command line "
        "switches, do a dry-run and print the example config file "
        "contents to stdout."
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install the example config file unless you have one already",
    )
    args = parser.parse_args()

    prefix = "Copying" if args.install else "Would copy"
    print("{} {} to {}".format(prefix, SAMPLE_CONFIG_FILENAME, CONFIG_FILENAME))
    if args.install:
        message = "Not installing, config file already in place: {}".format(
            CONFIG_FILENAME
        )
        error_if(os.path.exists(CONFIG_FILENAME), message=message)
        shutil.copy(SAMPLE_CONFIG_FILENAME, CONFIG_FILENAME)
    else:
        with open(SAMPLE_CONFIG_FILENAME) as input:
            shutil.copyfileobj(input, sys.stdout)
