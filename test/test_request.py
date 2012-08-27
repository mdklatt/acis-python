import unittest

import local
from acis import *

class TestRequest(unittest.TestCase):

    def setUp(self):
        self.request = Request("StnData")
        self.params = { "sid": "346661", "elems": "maxt", "date": "20090101",
            "meta": "uid" }
        self.result = { "meta": { "uid": 92 }, "data": [["2009-01-01","57"]] }
        return

    def test_init(self):
        """ Test normal init. """
        url = "http://data.rcc-acis.org/StnData"
        self.assertEqual(self.request._url, url)
        return

    def test_submit(self):
        """ Test normal submit. """
        response = { "params": self.params, "result": self.result }
        self.assertEqual(self.request.submit(self.params), response)
        return

    def test_submit_fail(self):
        """ Test submit failure. """
        self.params.pop("sid")
        self.assertRaises(RequestError, self.request.submit, self.params)
        return


class TestRequestError(unittest.TestCase):

    def setUp(self):
        self.code = 400
        self.text = "An error occurred"
        return

    def test_text(self):
        """ Test a plain text error message. """
        error = RequestError(self.text, self.code)
        self.assertEqual(error.message, self.text)
        return

    def test_html(self):
        """ Test an HTML error message. """
        html = "<html>\n<body>\n<p>%s</p>\n</body\n</html>" % self.text
        error = RequestError(html, self.code)
        self.assertEqual(error.message, self.text)
        return

    def test_code(self):
        """ Test the status code. """
        error = RequestError(self.text, self.code)
        self.assertEqual(error.code, self.code)


if __name__ == "__main__":
    unittest.main()
