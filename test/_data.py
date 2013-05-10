from ast import literal_eval
from copy import deepcopy
from json import loads
from os import chdir
from os import getcwd
from os.path import dirname
from xml.etree.ElementTree import parse


class TestData(object):
    """ Data for a specfic test case.
    
    The data can be used in multiple test without worrying about any side
    effects.    
    
    """
    _conversions = { 
        # Conversions for non-native data types.
        "json": loads}  # native type will be a dict

    def __init__(self, data_file):
        """ Initialize this object. 
        
        """
        cwd = getcwd()
        try:
            chdir(dirname(__file__))        
            self._data = {}
            root = parse(data_file)
            for elem in root.findall("value"):
                name, dtype = elem.get("name"), elem.get("dtype")
                convert = self._conversions.get(dtype, literal_eval)
                self._data[name] = convert(elem.text.strip())
        finally:
            # Restore the original working directory no matter what.
            chdir(cwd)
        return
            
    def __getattr__(self, name):
        """ Return a data attribute.
                
        """
        # A deep copy is returned so that all values are independent.
        try:
            return deepcopy(self._data[name])
        except KeyError:
            raise AttributeError("unknown value: '{0:s}'".format(name))
