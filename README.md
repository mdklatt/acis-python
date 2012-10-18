acis-python
========

Overview
--------
The [acis-python][1] library provides tools for [ACIS Web Services][5] client 
applications. There is also a [PHP version][7].


Requirements
------------
* Python 2.6 - 2.7
* [dateutil][8]
* [numpy][9] (optional; required for `result_array()` function)
* [unittest2][10] (optional; required to run tests with Python 2.6)

Requirements can be installed using `pip`:

    pip install -r requirements.txt
    pip install -r optional-requirements.txt

Installation
------------
Place the [acis][2] directory in the Python [module search path][6]. The 
[setup script][4] can be used to install the library in the user or system 
`site-packages` directory.

    python setup.py install --user  # install for the current user

Usage
-----
The library requires a single import:

    import acis
        
The [tutorial][3] has examples of how to use the library.
        
Known Issues/Limitations
------------------------
* MultiStnDataResult will give the wrong dates when iterating over "groupby" results.


<!-- REFERENCES -->
[1]: http://github.com/mdklatt/acis-python "acis-python"
[2]: http://github.com/mdklatt/acis-python/tree/master/acis "acis"
[3]: http://github.com/mdklatt/acis-python/blob/master/doc/tutorial.py "tutorial"
[4]: https://github.com/mdklatt/acis-python/blob/master/setup.py "setup"
[5]: http://data.rcc-acis.org "ACIS WS"
[6]: http://docs.python.org/tutorial/modules.html#the-module-search-path "Python import"
[7]: http://github.com/mdklatt/acis-php "acis-php"
[8]: http://labix.org/python-dateutil "dateutil"
[9]: http://numpy.scipy.org "numpy"
[10]: http://pypi.python.org/pypi/unittest2 "unittest2"