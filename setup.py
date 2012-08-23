"""
Distutils setup script for the utillib.chron module.

"""
import sys
from distutils.core import setup

def main():
	dist = {
		'name': 'acis',
		'version': '0.1.dev',
		'author': 'Michael Klatt',
		'author_email': 'mdklatt@ou.edu',
		'packages': ['acis'],
	}
	setup(**dist)
	return 0


if __name__ == '__main__':
	sys.exit(main())
