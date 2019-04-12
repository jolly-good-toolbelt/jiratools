Some simple API functions and command-line tools for interacting with JIRA.


Setup
-----
All the tools and functions here need your specific information from
a ``jira.config`` file in your home directory, so you have to do this setup
before anything can be used:

* run ``jira-example-config --install`` to install an example config file
  (you can run it without ``--install`` to see the contents of what would be
  installed. (If you already have a ``jira.config`` in your home directory,
  this script will `not` overwrite it.)
* Fill out the values in the config file with your appropriate data
  (see the comments in that file for guidance).


Command-Line Tools
------------------

``jira-example-config`` can install an example config file for you, see above.

``jira-make-linked-issue`` makes a new JIRA issue that is linked to an exisiting issue;
the new issue's fields can be set from defaults in your ``jira.config``
or those values can be overridden on the command line.
See ``--help`` on this command for all the command line options,
and the comments in ``jira.config`` for setting the defaults.

``jira-add-comment`` adds a comment to a JIRA issue.
The ``jira.config`` file is needed to authenticate to JIRA.
No other data from the ``jira.config`` file is used by this commmand.
See ``--help`` on this command for details. You can also use ``-`` as your comment
and ``jira-add-comment`` will read the comment from stdin instead. Note that if you
use ``-`` interactively, you cannot edit your comment before it is posted.

``jira-search-issues`` searches JIRA using your JQL query.
The ``jira.config`` file is needed to authenticate to JIRA.
You may set a default integer max_results value
as ``MAX_RESULT_COUNT`` in ``jira.config``,
or set a value of ``-1`` for no max by default.
See ``--help`` on this command for details.

``jira-link-issues`` creates a link between two issues.
The ``jira.config`` is needed to authenticate to JIRA.


Error Logging Tools
-------------------

These functions are designed to be used within Python code
to assist with various error commenting logic.

* ``jiratools.error_logging.add_jira_error_comment`` can take an error
  and add a formatted comment to a relevant JIRA issue

* ``jiratools.error_logging.add_jira_comment_with_table`` can add a comment
  with a formatted data table to a jira issue

* ``jiratools.error_logging.update_jira_for_errors`` can check found errors
  against a list of JIRA issues
  and add comments to any JIRA issues where a match is found.


Formatting Tools
----------------

These functions are designed to be used within Python code
to assist with comment formatting logic.

* ``jiratools.formatting.format_autoupdate_jira_msg`` takes a message body
  and add relevant title/header data

* ``jiratools.formatting.format_as_jira_table`` takes headers and table rows
  and formats a JIRA-style table


Examples
~~~~~~~~

* ``jira-add-comment JIRA-1234 "Work in Progress. PR delayed by network problems."``
  -- Add the comment to JIRA-1234 using the user/password from your ``jira.config``
  Note that the comment has to be just one command line argument surrounded by quotes
  if it contains spaces, etc.
* ``jira-make-linked-issue JIRA-1234``
  -- will create a JIRA in your ``TEST_PROJECT`` to test JIRA-1234,
  and link the two, assigning it to you and
  adding any watchers specified in your default watchers list.
* ``jira-make-linked-issue JIRA-1234 --project OTHER``
  -- will create a test JIRA as above, but in ``OTHER``
* ``jira-make-linked-issue JIRA-1234 --user bobm5523``
  -- will create the JIRA as above, but assign to ``bobm5523``
* ``jira-make-linked-issue JIRA-1234 -w sall9987 -w benj4444``
  -- will create the JIRA and assign ``sall9987`` and ``benj4444`` as watchers
  instead of your default watcher list
* ``jira-search-issues "project=ABC AND summary ~ client"``
  -- will print a list of links and titles for issues in project ABC
  that include the word "client" in the summary.
* ``jira-link-issues ABC-123 XYZ-456``
  -- will create a link such that ``ABC-123`` relates to ``XYZ-456``
