"""Build Example Config."""
import os
import shutil
import sys

from jgt_common import error_if

from .utils import CONFIG_FILENAME, SAMPLE_CONFIG_FILENAME


def cli_example_config(install: bool, install_if_missing: bool) -> None:
    """Build example config."""
    error_if(
        not os.path.exists(SAMPLE_CONFIG_FILENAME),
        message="Missing example config file: {}".format(SAMPLE_CONFIG_FILENAME),
    )

    prefix = "Copying" if install else "Would copy"
    print("{} {} to {}".format(prefix, SAMPLE_CONFIG_FILENAME, CONFIG_FILENAME))

    if install or install_if_missing:
        config_exists = os.path.exists(CONFIG_FILENAME)
        message = "Not installing, config file already in place: {}".format(
            CONFIG_FILENAME
        )
        if install:
            error_if(config_exists, message=message)
        elif install_if_missing:
            print(message)
            exit()
        shutil.copy(SAMPLE_CONFIG_FILENAME, CONFIG_FILENAME)
    else:
        with open(SAMPLE_CONFIG_FILENAME) as in_file:
            shutil.copyfileobj(in_file, sys.stdout)
