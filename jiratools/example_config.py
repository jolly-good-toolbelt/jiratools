"""Build Example Config."""
import argparse
import os
import shutil
import sys

from jgt_common import error_if

from .utils import CONFIG_FILENAME, SAMPLE_CONFIG_FILENAME


def cli_example_config(args: argparse.Namespace) -> None:
    """Build example config."""
    error_if(
        not os.path.exists(SAMPLE_CONFIG_FILENAME),
        message="Missing example config file: {}".format(SAMPLE_CONFIG_FILENAME),
    )

    prefix = "Copying" if args.install else "Would copy"
    print("{} {} to {}".format(prefix, SAMPLE_CONFIG_FILENAME, CONFIG_FILENAME))
    if args.install:
        message = "Not installing, config file already in place: {}".format(
            CONFIG_FILENAME
        )
        error_if(os.path.exists(CONFIG_FILENAME), message=message)
        shutil.copy(SAMPLE_CONFIG_FILENAME, CONFIG_FILENAME)
    else:
        with open(SAMPLE_CONFIG_FILENAME) as in_file:
            shutil.copyfileobj(in_file, sys.stdout)
