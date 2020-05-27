## jamf-package-clean

__Still under active development__

## list.py

Finds the packages not used by policies and patch policies
in your Jamf DP and lists them to stdout. It lists the package id followed by a tab then the package name.

Usage:`list.py > unused.txt`

## remove.py

Reads a list of packages from stdin and removes them. It assumes the same format that is produced by `list.py`. Safe
practice might be to check the list from `list.py` before feeding it to `remove.py`, I certainly do.

Usage:`remove.py < unused.txt`
