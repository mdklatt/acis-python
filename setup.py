"""
Distutils setup script for the acis library.

"""
import distutils.core
import sys

def main():
    dist = {
        "name":         "acis",
        "version":      "0.1.dev",
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
