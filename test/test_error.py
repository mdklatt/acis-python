import unittest

import local
from acis import *


class RequestErrorTest(unittest.TestCase):

    def test_init(self):
        """ Test error message. """
        message = "an error occurred"
        error = RequestError(message)
        self.assertEqual(error.message, message)
        return


class ParameterErrorTEst(unittest.TestCase):

    def test_init(self):
        """ Test error message. """
        message = "bad parameters"
        error = RequestError(message)
        self.assertEqual(error.message, message)
        return


class ResultErrorTest(unittest.TestCase):

    def test_init(self):
        """ Test aerror message. """
        message = "An error occurred"
        error = ResultError(message)
        self.assertEqual(error.message, message)
        return


if __name__ == "__main__":
    unittest.main()
