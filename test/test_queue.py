""" Testing for the the queue.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest
from _data import TestData

from acis import StnDataRequest
from acis import StnDataResult
from acis.queue import RequestQueue


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class RequestQueueTest(unittest.TestCase):
    """ Unit testing for the RequestQueue class.

    """
    @classmethod
    def setUpClass(cls):
        """ Initialize the RequestQueueTest class.

        This is called before any tests are run. This is part of the unittest
        API.

        """
        cls._DATA = TestData("data/StnData.xml")
        return

    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        params = self._DATA.params
        result = self._DATA.result
        self._query = {"params": params, "result": result}
        self._request = StnDataRequest()
        self._request.location(sid="okc")
        self._request.dates("2011-12-31", "2012-01-01")
        self._request.add_element("mint", smry="min")
        self._request.add_element(1, smry="max")  
        self._request.metadata("county", "name")
        #self._result = StnDataResult(self._query)
        return
        
    def test_execute(self):
        """ Test the execute method.
        
        """
        queue = RequestQueue()
        queue.add(self._request)
        queue.add(self._request)
        queue.execute()
        for item in queue.results:
            self.assertDictEqual(self._query["result"], item["result"])
        return

    def test_execute_callback(self):
        """ Test the execute method with a callback.
        
        """
        queue = RequestQueue()
        queue.add(self._request, StnDataResult)
        queue.add(self._request, StnDataResult)
        queue.execute()
        result = StnDataResult(self._query)
        for item in queue.results:
            # self.assertDictEqual(result.meta, item.meta)
            self.assertDictEqual(result.data, item.data)
            # self.assertDictEqual(result.smry, item.smry)
        return
    
    def test_clear(self):
        queue = RequestQueue()
        queue.add(self._request)
        queue.execute()
        queue.clear()
        queue.execute()
        self.assertEqual(0, len(queue.results))
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (RequestQueueTest,)

def load_tests(loader, tests, pattern):
    """ Define a TestSuite for this module.

    This is part of the unittest API. The last two arguments are ignored. The
    _TEST_CASES global is used to determine which TestCase classes to load
    from this module.

    """
    suite = unittest.TestSuite()
    for test_case in _TEST_CASES:
        tests = loader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    return suite


# Make the module executable.

if __name__ == "__main__":
    unittest.main()  # main() calls sys.exit()
