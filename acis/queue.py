""" Parallel execution of multiple ACIS Requests.

*USE AT YOUR OWN RISK.*  

In situations where server-side processing is the bottleneck, application
performance can be enhanced by executing requests in parallel on the ACIS
server.

This is _very_ alpha and cannot handle things like server redirects (but ACIS
isn't doing this...yet). An error with one request will take the whole queue
down. The way it hooks into Request objects required very little modification 
of request.py (and those changes were good regardless), but it still seems 
kludgy. The interface should not be considered stable. 

"""
import asyncore
import cStringIO
import json
import socket
import urllib
import urlparse

from acis import RequestError
from acis import ResultError


class RequestQueue(object):
    """ Manage parallel Requests.
    
    """
    @staticmethod
    def _parse(reply):
        """ Retrieve the JSON result from the reply returned by the server.
        
        """
        # TODO: This was mostly pulled from call.py so some refactoring is in
        # order.
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
            return json.loads(reply.content)
        except ValueError:
            raise ResultError("server returned invalid JSON")
        
    def __init__(self):
        """ Initialize a RequestQueue object.
        
        """
        self._sockets = {}
        self._queue = []
        self._results = []
        pass
        
    def add(self, request, result_type=None):
        """ Add a Request to the queue.
        
        The optional result paramater can be a Result class or anything that
        accepts a query object as an argument.
        
        """
        url = urlparse.urlparse(request._call.url)
        data = urllib.urlencode({"params": json.dumps(request.params)})
        http_request = _HttpRequest(url.netloc, url.path, data, self._sockets)
        self._queue.append((http_request, request.params, result_type))
        return
        
    def execute(self):
        """ Execute all requests in the queue.
        
        When execution is complete, each element of the queue will contain a
        query object or the optional result type specified for that request.
        
        """
        asyncore.loop(map=self._sockets)  # execute all requests in this queue
        for http_request, params, result_type in self._queue:
            try:
                json_result = self._parse(http_request)
            except:
                # Need to do something about exceptions so that a single error
                # doesn't take the entire queue down, but punt for now. 
                raise
            query = {"params": params, "result": json_result}
            if result_type is None:
                self._results.append(query)
            else:
                self._results.append(result_type(query))
        return
        
    def __iter__(self):
        """ Iterate over all results in the queue.
        
        """
        return iter(self._results)
        
    def __getitem__(self, key):
        """ Array access to individual results in the queue.
        
        """
        return self._results[key]
        
        
class _HttpRequest(asyncore.dispatcher):
    """ A single asynchronous HTTP request.

    """
    @staticmethod
    def _post(path, data):
        """ Generate a POST request string.
        
        """
        crlf = "\r\n"
        post = ["POST {0:s} HTTP/1.0".format(path)]
        post.append("Content-Type: application/x-www-form-urlencoded")
        post.append("Content-Length: {0:d}".format(len(data)))
        post.append("")
        post.append(data)
        return crlf.join(post)
        
    def __init__(self, host, path, data, map):
        """ Initialize an _HttpRequest object.
        
        """
        asyncore.dispatcher.__init__(self, map=map)
        self.status = (-1, "")
        self.content = None
        self._buffer = cStringIO.StringIO()
        self._request = self._post(path, data)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, 80))
        return

    def _reply(self):
        """ Parse the reply from the server.
        
        """
        # The reply should consist of a status line, header lines (ignored)
        # followed by a blank line, and then the content.
        http, code, message = self._buffer.readline().rstrip().split(" ", 2)
        self.status = (int(code), message)
        for header in self._buffer:
            if not header.rstrip():
                break
        self.content = self._buffer.read()
        return

    # Implement the asyncore.dispatcher interface.
    
    def writable(self):
        """ Return True while there are data to send to the server.
        
        """
        return len(self._request) > 0
        
    def handle_write(self):
        """ Send data to the server.
        
        """
        # There's no guarantee that all of the data will be sent as a single
        # chunk, so repeat until there is nothing left to send.
        #print self._request
        count = self.send(self._request)
        self._request = self._request[count:]
        return
        
    def readable(self):
        """ Return True while interested in reading data from the server.
        
        """
        return True  # retrieve all data from the server
        
    def handle_read(self):
        """ Write data from the server to a buffer.
        
        """
        self._buffer.write(self.recv(8192))
        return
        
    def handle_close(self):
        """ The server has closed the connection, so parse the request.
        
        """
        self.close()
        self._buffer.seek(0)
        self._reply()
        return
        
    # def handle_error(self):
    #     # Catch exceptions here so a single error doesn't take the whole queue
    #     # down. Or something. Not sure how this works yet.        
    #     return
        

