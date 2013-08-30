""" Parallel execution of multiple ACIS Requests.

* USE AT YOUR OWN RISK. *  

In situations where server-side processing is the bottleneck, application
performance can be enhanced by executing requests in parallel on the ACIS
server.

This is _very_ alpha and cannot handle things like server redirects (but ACIS
isn't doing this...yet). An error with one request will take the whole queue
down. The interface should not be considered stable. 

"""
from __future__ import absolute_import

from asyncore import dispatcher
from asyncore import loop
from cStringIO import StringIO
from json import dumps
from json import loads
from socket import AF_INET
from socket import SOCK_STREAM
from urllib import urlencode
from urlparse import urlparse

from acis import RequestError
from acis import ResultError


class RequestQueue(object):
    """ Manage parallel Requests.
    
    """
    @staticmethod
    def _parse(reply):
        """ Retrieve the JSON result from the reply returned by the server.
        
        """
        code, message = reply.status
        if code != 200:
            # This doesn't do the right thing for a "soft 404", e.g. an ISP
            # redirects to a custom error or search page for a DNS lookup
            # failure and returns a 200 (OK) code.
            if code == 400:
                # If the ACIS server returns this code it also provides a
                # helpful plain text error message as the content.
                raise RequestError(reply.content.rstrip())
            else:
                error = "HTTP error: {0:s} ({1:d})".format(message, code)
                raise RuntimeError(error)
        try:
            return loads(reply.content)
        except ValueError:
            raise ResultError("server returned invalid JSON")
        
    def __init__(self):
        """ Initialize a RequestQueue object.
        
        """
        self.clear()
        return
        
    def add(self, request, callback=None):
        """ Add a Request to the queue.
        
        During execution the resulting query object is passed to callback and
        the return value is stored; if no callback is specified the query
        object is stored.
                
        """
        url = urlparse(request.url)
        data = urlencode({"params": dumps(request.params)})
        http_request = _HttpRequest(url.netloc, url.path, data, self._sockmap)
        self._queue.append((http_request, request.params, callback))
        return
        
    def execute(self):
        """ Execute all requests in the queue.
        
        When execution is complete each element of the results attribute will 
        contain a query object or the optional result type specified for that 
        request.
        
        """
        loop(map=self._sockmap)  # execute all requests in this queue
        for http_request, params, callback in self._queue:
            try:
                result = self._parse(http_request)
            except:
                # Need to do something about exceptions so that a single error
                # doesn't take the entire queue down, but punt for now. 
                raise
            query = {"params": params, "result": result}
            try:
                self.results.append(callback(query))                
            except TypeError:  # no callback
                self.results.append(query)                
        return
    
    def clear(self):
        """ Clear all requests and results in the queue.
        
        """
        self.results = []
        self._sockmap = {}
        self._queue = []
        return
        
        
class _HttpRequest(dispatcher):
    """ A single asynchronous HTTP request.

    """    
    @staticmethod
    def _post(path, data):
        """ Generate a POST request string.
        
        """
        CRLF = "\r\n"
        post = ["POST {0:s} HTTP/1.0".format(path)]
        post.append("Content-Type: application/x-www-form-urlencoded")
        post.append("Content-Length: {0:d}".format(len(data)))
        post.append("")
        post.append(data)
        return CRLF.join(post)
        
    def __init__(self, host, path, data, map):
        """ Initialize an _HttpRequest object.
        
        """
        dispatcher.__init__(self, map=map)
        self.status = None
        self.content = None
        self._buffer = StringIO()
        self._request = self._post(path, data)
        self.create_socket(AF_INET, SOCK_STREAM)
        # Connection fails with with a socket.gaierror exception ("nodename nor
        # servname provided, or not known") for more than 248 open connections;
        # perhaps the ACIS server fails to respond if there are too many 
        # connections from one client.
        self.connect((host, 80))
        return

    def _reply(self):
        """ Parse the reply from the server.
        
        """
        # The reply should consist of a status line, header lines (ignored)
        # followed by a blank line, and then the content.
        status = self._buffer.readline().rstrip().split(" ", 2)
        code, message = status[1:]
        self.status = (int(code), message)
        for header in self._buffer:
            if not header.rstrip():
                break
        self.content = self._buffer.read()
        return

    # Implement the dispatcher interface.
    
    def writable(self):
        """ Return True while there are data to send to the server.
        
        """
        return len(self._request) > 0
        
    def handle_write(self):
        """ Send a chunk of data to the server.
        
        """
        count = self.send(self._request)
        self._request = self._request[count:]
        return
        
    def readable(self):
        """ Return True while interested in reading data from the server.
        
        """
        return True  # retrieve all data from the server
        
    def handle_read(self):
        """ Read a chunk of data from the server.
        
        """
        # The chunk size was chosen arbitrarily so there may be room for some
        # optimization, but any bottleneck is almost certainly going to be on 
        # the server, not during data transfer.
        self._buffer.write(self.recv(8192))
        return
        
    def handle_close(self):
        """ The server has closed the connection, so parse the reply.
        
        """
        self.close()
        self._buffer.seek(0)
        self._reply()
        return
        
    # def handle_error(self):
    #     # Catch exceptions here so a single error doesn't take the whole queue
    #     # down. Or something. Not sure how this works yet.        
    #     pass
        

