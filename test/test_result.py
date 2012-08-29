import datetime
import unittest

import local
from acis import *

class TestStnMetaResult(unittest.TestCase):

    def setUp(self):
        self.request = Request("StnMeta")
        return

    def test_init(self):
        """ Test init. """
        params = { "sids": "OKC", "meta": ( "uid", "county" ) }
        result = StnMetaResult(self.request.submit(params))
        self.assertEqual(result.meta, {  92: { "county": "40109" } })
        return

    def test_init_fail(self):
        """ Test init failure (no uid). """
        params = { "sids": "OKC", "meta": "county" }
        response = self.request.submit(params)
        self.assertRaises(ValueError, StnMetaResult, response)
        return


class TestStnDataResult(unittest.TestCase):

    def setUp(self):
        params = { "sid": "OKC", "sdate": "20090101", "edate": "20090103",
            "elems": "maxt", "meta": ("uid", "county") }
        self.result = StnDataResult(Request("StnData").submit(params))
        return

    def test_meta(self):
        """ Test init. """
        self.assertEqual(self.result.meta, {  92: { "county": "40109" } })
        return

    def test_len(self):
        self.assertEqual(len(self.result), 3)
        return

    def test_iter(self):
        records = (
            (92, datetime.date(2009, 1, 1), "57"),
            (92, datetime.date(2009, 1, 2), "49"),
            (92, datetime.date(2009, 1, 3), "73"),
        )
        for i, record in enumerate(self.result):
            self.assertEqual(record.uid, records[i][0])
            self.assertEqual(record.date, records[i][1])
            self.assertEqual(record.maxt, records[i][2])
        return

    def test_data(self):
        data = { 92: [["2009-01-01","57"], ["2009-01-02","49"],
            ["2009-01-03","73"]] }
        self.assertEqual(self.result.data, data)
        return

    def test_no_uid(self):
        """ Test init failure (no uid). """
        params = { "sid": "OKC", "date": "20090101", "elems": "maxt",
            "meta": "county" }
        response = Request("StnData").submit(params)
        self.assertRaises(ValueError, StnDataResult, response)
        return

    def test_result_error(self):
        response = { "result": { "error": "error message" } }
        self.assertRaises(ResultError, StnDataResult, response)
        return


class TestMultiStnDataResult(unittest.TestCase):

    def setUp(self):
        params = { "sids": "OKC,TUL", "sdate": "20090101", "edate": "20090103",
            "elems": "maxt", "meta": ("uid", "county") }
        request = Request("MultiStnData")
        self.result = MultiStnDataResult(request.submit(params))
        return

    def test_meta(self):
        """ Test init. """
        meta = { 92: { "county": "40109" }, 14134: { "county": "40143" } }
        self.assertEqual(self.result.meta, meta)
        return

    def test_len(self):
        self.assertEqual(len(self.result), 6)
        return

    def test_iter(self):
        records = [
            (92, datetime.date(2009, 1, 1), "57"),
            (92, datetime.date(2009, 1, 2), "49"),
            (92, datetime.date(2009, 1, 3), "73"),
            (14134, datetime.date(2009, 1, 1), "53"),
            (14134, datetime.date(2009, 1, 2), "58"),
            (14134, datetime.date(2009, 1, 3), "78"),
        ]
        for i, record in enumerate(self.result):
            self.assertEqual(record.uid, records[i][0])
            self.assertEqual(record.date, records[i][1])
            self.assertEqual(record.maxt, records[i][2])
        return

    def test_data(self):
        data = { 92: [["57"],["49"],["73"]], 14134: [["53"],["58"],["78"]] }
        self.assertEqual(self.result.data, data)
        return

    def test_no_uid(self):
        """ Test init failure (no uid). """
        params = { "sids": "OKC", "date": "20090101", "elems": "maxt",
            "meta": "county" }
        response = Request("MultiStnData").submit(params)
        self.assertRaises(ValueError, MultiStnDataResult, response)
        return

    def test_result_error(self):
        response = { "result": { "error": "error message" } }
        self.assertRaises(ResultError, MultiStnDataResult, response)
        return


class TestResultError(unittest.TestCase):

    def test_init(self):
        """ Test aerror message. """
        message = "An error occurred"
        error = ResultError(message)
        self.assertEqual(error.message, message)
        return


if __name__ == "__main__":
    unittest.main()
