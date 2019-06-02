import os
import setuptools

NAME = "jiratools"
DESCRIPTION = "Simple helpers to interface to JIRA from an API or command line."
VERSION = None

CONSOLE_SCRIPTS = [
    "jira-make-linked-issue=jiratools:_create_test_jira_from",
    "jira-add-comment=jiratools:_cli_add_comment",
    "jira-example-config=jiratools:_example_config_install",
    "jira-search-issues=jiratools:_cli_search",
    "jira-link-issues=jiratools:cli_jira_link",
    "jira-update-assignee=jiratools:_change_jira_assignee",
]

INSTALL_REQUIRES = [
    "jira",
    'configparser ; python_version<"3.5"',  # backport required for py2 compatibility
]

EXTRAS_REQUIRE = {"dev": ["flake8", "black"]}

here = os.path.abspath(os.path.dirname(__file__))

about = {}
if not VERSION:
    with open(os.path.join(here, NAME, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


with open(os.path.join(here, "README.rst")) as f:
    long_description = f.read()


setuptools.setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    url="https://github.com/bradsbrown/jiratools",
    author="Brad Brown",
    author_email="brad@bradsbrown.com",
    license="MIT",
    entry_points={"console_scripts": CONSOLE_SCRIPTS},
    install_requires=INSTALL_REQUIRES,
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require=EXTRAS_REQUIRE,
)
