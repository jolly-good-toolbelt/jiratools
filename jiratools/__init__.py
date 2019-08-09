"""Some simple API functions and command-line tools for interaction with JIRA."""

from __future__ import print_function
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
    RawDescriptionHelpFormatter,
)

from .utils import ConfigNotFoundException, CONFIG, load_config, DEFAULT_LINK_TYPE
from .helpers import list_from_config

from .comment import cli_add_comment
from .link import cli_jira_link
from .make_linked import cli_make_linked
from .search import cli_search
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
    """Linke two JIRA from cli."""
    parser = _setup_link_parser(
        ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    )
    args = parser.parse_args()
    cli_jira_link(args)


def _setup_make_linked_parser(parser: ArgumentParser) -> ArgumentParser:
    load_config()
    if not CONFIG:
        raise ConfigNotFoundException
    parser.add_argument("jira_id")
    assign_default = bool(CONFIG["DEFAULT_ASSIGNEE"])
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
        default=list_from_config("DEFAULT_COMPONENTS"),
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
        default=list_from_config("DEFAULT_LABELS"),
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
        default=list_from_config("WATCHERS"),
        help="Watchers to add to Test JIRA",
    )
    return parser


def make_linked() -> None:
    """Make a JIRA linked to the given one."""
    parser = _setup_make_linked_parser(
        ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    )
    cli_make_linked(parser.parse_args())


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
    cli_add_comment(parser.parse_args())


def _setup_search_parser(parser):
    if not CONFIG:
        raise ConfigNotFoundException
    default_max_count = int(CONFIG.get("MAX_RESULT_COUNT", "0")) or 10
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
    """Place JQL search and return results."""
    parser = _setup_search_parser(
        ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    )
    cli_search(parser.parse_args())


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
    cli_reassign(parser.parse_args())


def _setup_config_parser(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install the example config file unless you have one already",
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
    cli_example_config(parser.parse_args())


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
    args.func(args)
