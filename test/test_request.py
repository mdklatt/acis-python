import sys
import unittest

import local
from acis import *

class TestRequest(unittest.TestCase):

    def setUp(self):
        self.request = Request("StnData")
        self.params = { "sid": "OKC", "elems": "maxt", "date": "20090101",
            "meta": "uid" }
        self.result = { "meta": { "uid": 92 }, "data": [["2009-01-01","57"]] }
        return

    def test_init(self):
        """ Test normal init. """
        url = "http://data.rcc-acis.org/StnData"
        self.assertEqual(self.request.url, url)
        return

    def test_submit(self):
        """ Test normal submit. """
        response = { "params": self.params, "result": self.result }
        self.assertEqual(self.request.submit(self.params), response)
        return

    def test_submit_bad_request(self):
        """ Test submit failure. """
        self.params.pop("sid")
        self.assertRaises(RequestError, self.request.submit, self.params)
        return


class TestRequestError(unittest.TestCase):

    def test_init(self):
        """ Test error message. """
        message = "an error occurred"
        error = RequestError(message)
        self.assertEqual(error.message, message)
        return


if __name__ == "__main__":
    sys.exit(unittest.main())
