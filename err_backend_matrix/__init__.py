"""__init__.py"""

import os


def plugin_dir() -> str:
    """Return the location of the plugin dir for errbot."""
    return os.path.dirname(__file__)
