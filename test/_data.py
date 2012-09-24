import ast
import copy
import json
import xml.etree.ElementTree


class TestData(object):
    """ Data for a specfic test case.
    
    The data can be used in multiple test without worrying about any side
    effects.    
    
    """
    _conversions = { 
        # Conversions for non-native data types.
        "json": json.loads,  # native type will be a dict
    }

    def __init__(self, data_file):
        """ Initialize a TestScenario object. 
        
        """        
        self._data = {}
        root = xml.etree.ElementTree.parse(data_file)
        for elem in root.iterfind("value"):
            name, dtype = elem.get("name"), elem.get("dtype")
            convert = self._conversions.get(dtype, ast.literal_eval)
            self._data[name] = convert(elem.text.strip())
        return
            
    def __getattr__(self, name):
        # A deep copy is returned so that all values are independent.
        try:
            return copy.deepcopy(self._data[name])
        except KeyError:
            raise AttributeError("unknown value: '{0:s}'".format(name))
