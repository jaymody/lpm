"""Main entrypoint for Lines Per Minute.

Use `lpm -h` for help.
"""

import sys

if sys.version_info < (3, 6):
    print("ERROR: lpm requires python >= 3.6")
    sys.exit()

from .commandline import cli

if __name__ == "__main__":
    cli()
