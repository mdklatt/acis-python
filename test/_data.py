import copy
import json
import xml.etree.ElementTree
import unittest


class TestData(object):
    """ Data for a specfic test case.
    
    The data can be used in multiple test without worrying about any side
    effects.    
    
    """
    _convert = { 
        # Conversions for non-native data types.
        "json": json.loads,  # native type will be a dict
    }

    def __init__(self, data_file):
        """ Initialize a TestScenario object. 
        
        """        
        self._data = {}
        root = xml.etree.ElementTree.parse(data_file)
        for elem in root.iterfind("value"):
            dtype = elem.get("dtype")
            try:     
                value = TestData._convert[dtype](elem.text)
            except KeyError:  # use a native conversion
                value = eval("{0:s}({1:s})".format(dtype, elem.text))
            self._data[elem.get("name")] = value
        return
            
    def __getattr__(self, name):
        # A deep copy is returned so that all values are independent.
        try:
            return copy.deepcopy(self._data[name])
        except KeyError:
            raise AttributeError("unknown value: '{0:s}'".format(name))
