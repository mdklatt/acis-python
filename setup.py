""" Distutils setup script for the acis library.

Basic command to run the test suite and install library in the user's package
directory if all tests pass:

    python setup.py test install --user

"""
from distutils.core import Command
from distutils.core import setup
from sys import exit

from acis import __version__
from test import run as run_tests

SETUP_CONFIG = {
    "name":         "acis",
    "packages":     ("acis",),
    "requires":     ("dateutil",),
    "author":       "Michael Klatt",
    "author_email": "mdklatt@ou.edu",
    "url":          "https://github.com/mdklatt/acis-python",
    "version":      __version__}


class TestCommand(Command):
    """ Custom setup command to run the test suite.
    
    """
    description = "run the test suite"
    user_options = []
    
    def initialize_options(self):
        """ Set the default values for all options this command supports.
        
        """
        return
        
    def finalize_options(self):
        """ Set final values for all options this command supports.
        
        This is run after all other option assigments have been completed (e.g.
        command-line options, other commands, etc.)
        
        """
        return

    def run(self):
        """ Execute the command.
        
        """
        if run_tests() != 0:
            raise RuntimeError("test suite failed")
        return
        

def main():
    """ Execute the setup commands.
    
    """
    setup(cmdclass={"test": TestCommand}, **SETUP_CONFIG)
    return 0


# Make the script executable.

if __name__ == "__main__":
    exit(main())
