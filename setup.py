"""
Distutils setup script for the acis library.

For basic installation in the current user's site-packages directory:
    python setup.py install --user

"""
import distutils.core
import sys

from acis import __version__

def main():
    dist = {
        "name":         "acis",
        "version":      __version__,
        "packages":     ("acis",),
        "requires":     ("dateutil",),
        "author":       "Michael Klatt",
        "author_email": "mdklatt@ou.edu",
	    "url":          "https://github.com/mdklatt/acis-python",
    }
    distutils.core.setup(**dist)
    return 0


if __name__ == "__main__":
    sys.exit(main())
