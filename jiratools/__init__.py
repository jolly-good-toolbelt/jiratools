"""Some simple API functions and command-line tools for interaction with JIRA."""

from __future__ import print_function
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
    RawDescriptionHelpFormatter,
)

from .utils import load_config, DEFAULT_LINK_TYPE
from .helpers import list_from_config

from .comment import cli_add_comment
from .link import cli_jira_link
from .make_and_link import cli_make_linked
from .do_search import cli_search
from .assignee import cli_reassign
from .example_config import cli_example_config


def format_as_code_block(text_to_wrap: str) -> str:
    """
    Wrap the text in a JIRA code block.

    Args:
        text_to_wrap: The text to wrap.

    Returns:
        A JIRA formatted code block.

    """
    return "".join(["{code:java}", "{}".format(text_to_wrap), "{code}"])


def _setup_link_parser(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument("from_jira", help="The JIRA from which to create the link.")
    parser.add_argument("to_jira", help="The JIRA to which to create the link.")
    parser.add_argument(
        "-t",
        "--link-type",
        help="The type of link to create.",
        default=DEFAULT_LINK_TYPE,
    )
    return parser


def jira_link() -> None:
    """Link two JIRA from cli."""
    parser = _setup_link_parser(
        ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    )
    args = parser.parse_args()
    cli_jira_link(
        link_type=args.link_type, from_jira=args.from_jira, to_jira=args.to_jira
    )


def _setup_make_linked_parser(parser: ArgumentParser) -> ArgumentParser:
    config = load_config()
    parser.add_argument("jira_id")
    assign_default = bool(config["DEFAULT_ASSIGNEE"])
    assignment = parser.add_mutually_exclusive_group()
    assignment.add_argument(
        "--assign",
        dest="assign",
        default=assign_default,
        action="store_true",
        help="Assign story to user, current user if none provided.",
    )
    assignment.add_argument(
        "--no-assign",
        dest="assign",
        default=not assign_default,
        action="store_false",
        help="Leave Test JIRA unassigned",
    )
    parser.add_argument(
        "-p",
        "--project",
        default=config["TEST_PROJECT"],
        help="JIRA project in which to create test story",
    )
    parser.add_argument(
        "-u",
        "--user",
        default=config["DEFAULT_ASSIGNEE"],
        help="the user who will receive the assignment",
    )
    parser.add_argument(
        "-c",
        "--components",
        default=list_from_config("DEFAULT_COMPONENTS"),
        action="append",
        help="Component tag to be aplied to the Test Story",
    )
    parser.add_argument(
        "-d",
        "--description",
        default=config["DEFAULT_DESCRIPTION"],
        help="Description string for Test JIRA.",
    )
    parser.add_argument(
        "-l",
        "--labels",
        default=list_from_config("DEFAULT_LABELS"),
        action="append",
        help="Comma-separated list of labels to be applied to the Test story",
    )
    parser.add_argument(
        "-s",
        "--summary",
        default=config["DEFAULT_SUMMARY"],
        help="Summary string for Test JIRA - will receive the Dev JIRA key and "
        "summary as string format values",
    )
    parser.add_argument(
        "-t",
        "--issue-type",
        default=config["DEFAULT_ISSUE_TYPE"],
        help="Issue type for Test JIRA -- "
        "must be a valid type name on target project",
    )
    parser.add_argument(
        "-w",
        "--watchers",
        action="append",
        default=list_from_config("WATCHERS"),
        help="Watchers to add to Test JIRA",
    )
    return parser


def make_linked() -> None:
    """Make a JIRA linked to the given one."""
    parser = _setup_make_linked_parser(
        ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    )
    args = parser.parse_args()
    cli_make_linked(
        project=args.project,
        assign=args.assign,
        user=args.user,
        components=args.components,
        labels=args.labels,
        summary=args.summary,
        description=args.description,
        jira_id=args.jira_id,
        issue_type=args.issue_type,
        watchers=args.watchers
    )


def _setup_comment_parser(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument("jira_id")
    parser.add_argument("message", help="Comment to add to the given JIRA.")
    return parser


def add_comment() -> None:
    """
    Quick "add a short comment to a JIRA" command line tool.

    If 'message' is '-' then stdin will be read.
    """
    parser = _setup_comment_parser(
        ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter, description=add_comment.__doc__
        )
    )
    args = parser.parse_args()
    cli_add_comment(jira_id=args.jira_id, message=args.message)


def _setup_search_parser(parser):
    config = load_config()
    default_max_count = int(config.get("MAX_RESULT_COUNT", "0")) or 10
    default_max_count = False if default_max_count == -1 else default_max_count
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
    return parser


def search() -> None:
    """Perform JQL search and return results."""
    parser = _setup_search_parser(
        ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    )
    args = parser.parse_args()
    cli_search(
        query=args.query, max_results=args.max_results, count_only=args.count_only
    )


def _setup_reassign_parser(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument("jira_id")
    parser.add_argument("user", help="New assignee for the JIRA.")
    return parser


def reassign() -> None:
    """Assign JIRA to given user."""
    parser = _setup_reassign_parser(
        ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            description=cli_add_comment.__doc__,
        )
    )
    args = parser.parse_args()
    cli_reassign(jira_id=args.jira_id, user=args.user)


def _setup_config_parser(parser: ArgumentParser) -> ArgumentParser:
    install_settings = parser.add_mutually_exclusive_group()
    install_settings.add_argument(
        "--install",
        action="store_true",
        help="Install the example config file, raise an error if it already exists.",
    )
    install_settings.add_argument(
        "--install-if-missing",
        action="store_true",
        help="Install the example config file if it doesn't already exist.",
    )
    return parser


def example_config_install() -> None:
    """Build example config."""
    description = (
        "Install example jira.config in your homne directory "
        "unless you have one already. Without any command line "
        "switches, do a dry-run and print the example config file "
        "contents to stdout."
    )
    parser = _setup_config_parser(ArgumentParser(description=description))
    args = parser.parse_args()
    cli_example_config(install=args.install)


SUBPARSERS = {
    "link": (cli_jira_link, _setup_link_parser),
    "make-linked": (cli_make_linked, _setup_make_linked_parser),
    "comment": (cli_add_comment, _setup_comment_parser),
    "search": (cli_search, _setup_search_parser),
    "assign": (cli_reassign, _setup_reassign_parser),
    "make-config": (cli_example_config, _setup_config_parser),
}


def main() -> None:
    """Master jiratool command."""
    parser = ArgumentParser(
        description="For detailed help, provide the --help flag to a subcommand"
    )
    subparsers = parser.add_subparsers(title="subcommands")
    for name, (func, setup_parser) in SUBPARSERS.items():
        subparser = subparsers.add_parser(name)
        subparser = setup_parser(subparser)
        subparser.set_defaults(func=func)
    args = parser.parse_args()
    func_arg_dict = {k: v for k, v in vars(args).items() if k != "func"}
    args.func(**func_arg_dict)
