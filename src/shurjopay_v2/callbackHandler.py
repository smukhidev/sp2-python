from collections import namedtuple
from contextlib import closing
from io import BytesIO
from json import dumps as json_encode
import os
import sys
import requests
import json
import datetime
import logging
import os
# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)
# define file handler and set formatter
log_fileName = 'LOGS/{:%Y-%m-%d}.log'.format(datetime.datetime.now())
os.makedirs(os.path.dirname(log_fileName), exist_ok=True)
file_handler = logging.FileHandler(log_fileName, mode="a", encoding=None,)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(funcName)s  %(message)s')
file_handler.setFormatter(formatter)
# add file handler to logger
logger.addHandler(file_handler)

if sys.version_info >= (3, 0):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
    from urllib.parse import parse_qs
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn
    from urlparse import parse_qs

ResponseStatus = namedtuple("HTTPStatus",
                            ["code", "message"])

ResponseData = namedtuple("ResponseData",
                          ["status", "content_type", "data_stream"])

# Mapping the output format used in the client to the content type for the
# response
AUDIO_FORMATS = {"ogg_vorbis": "audio/ogg",
                 "mp3": "audio/mpeg",
                 "pcm": "audio/wave; codecs=1"}
CHUNK_SIZE = 1024
HTTP_STATUS = {"OK": ResponseStatus(code=200, message="OK"),
               "BAD_REQUEST": ResponseStatus(code=400, message="Bad request"),
               "NOT_FOUND": ResponseStatus(code=404, message="Not found"),
               "INTERNAL_SERVER_ERROR": ResponseStatus(code=500, message="Internal server error")}
PROTOCOL = "http"
RETURN_URL = "/return"
CANCEL_URL = "/cancel"


class HTTPStatusError(Exception):
    """Exception wrapping a value from http.server.HTTPStatus"""

    def __init__(self, status, description=None):
        """
        Constructs an error instance from a tuple of
        (code, message, description), see http.server.HTTPStatus
        """
        super(HTTPStatusError, self).__init__()
        self.code = status.code
        self.message = status.message
        self.explain = description


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """An HTTP Server that handle each request in a new thread"""
    daemon_threads = True


class ChunkedHTTPRequestHandler(BaseHTTPRequestHandler):
    """"HTTP 1.1 Chunked encoding request handler"""
    # Use HTTP 1.1 as 1.0 doesn't support chunked encoding
    protocol_version = "HTTP/1.1"

    verification_token = ''

    def query_get(self, queryData, key, default=""):
        """Helper for getting values from a pre-parsed query string"""
        return queryData.get(key, [default])[0]

    def do_HEAD(self):
        self.send_headers()

    def do_GET(self):
        """Handles GET requests"""

        # Extract values from the query string
        path, _, query_string = self.path.partition('?')
        query = parse_qs(query_string)

        response = None

        print(u"[START]: Received GET for %s with query: %s" % (path, query))

        try:
            # Handle the possible request paths
            if path == RETURN_URL:
                response = self.route_return(path, query)
            elif path == CANCEL_URL:
                response = self.route_cancel(path, query)
            else:
                response = self.route_not_found(path, query)

            self.send_headers(response.status, response.content_type)
            # self.stream_data(response.data_stream)
            logger.info(response)
            self._json(response.data_stream)

        except HTTPStatusError as err:
            # Respond with an error and log debug
            # information
            if sys.version_info >= (3, 0):
                self.send_error(err.code, err.message, err.explain)
            else:
                self.send_error(err.code, err.message)

            self.log_error(u"%s %s %s - [%d] %s", self.client_address[0],
                           self.command, self.path, err.code, err.explain)

        print("[END]")

    def route_not_found(self, path, query):
        """Handles routing for unexpected paths"""
        raise HTTPStatusError(HTTP_STATUS["NOT_FOUND"], "Page not found")

    def route_return(self, path, query):
        """Handles routing for the application's entry point'"""
        try:
            _POST_DEFAULT_ADDRESS = "https://sandbox.shurjopayment.com"
            _VERIFICATION_END_POINT = "/api/verification"
            # print('here!', query['order_id'][0])
            _headers = {'content-type': 'application/json', 'Authorization': f'Bearer {self.verification_token}'}
            _payloads = {
                "order_id": query['order_id'][0],
            }
            response = requests.post(_POST_DEFAULT_ADDRESS + _VERIFICATION_END_POINT, headers=_headers,
                                     data=json.dumps(_payloads))
            response_json = response.json()
            return ResponseData(status=HTTP_STATUS["OK"], content_type="application/json",
                                # Open a binary stream for reading the index
                                # HTML file
                                data_stream=response_json)
        except IOError as err:
            # Couldn't open the stream
            raise HTTPStatusError(HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                                  str(err))

    def route_cancel(self, path, query):
        """Handles routing for the application's entry point'"""
        try:
            return ResponseData(status=HTTP_STATUS["OK"], content_type="application/json",
                                # Open a binary stream for reading the index
                                # HTML file
                                data_stream=open(os.path.join(sys.path[0],
                                                              path[1:]), "rb"))
        except IOError as err:
            # Couldn't open the stream
            raise HTTPStatusError(HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                                  str(err))

    def send_headers(self, status, content_type):
        """Send out the group of headers for a successful request"""
        # Send HTTP headers

        self.send_response(status.code, status.message)
        self.send_header('Content-type', content_type)
        # self.send_header('Transfer-Encoding', 'chunked')
        # self.send_header('Connection', 'close')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def _json(self, response):
        str = json_encode(response)
        self.wfile.write(str.encode("utf8"))

    def stream_data(self, stream):
        """Consumes a stream in chunks to produce the response's output'"""
        print("Streaming started...")

        if stream:
            # Note: Closing the stream is important as the service throttles on
            # the number of parallel connections. Here we are using
            # contextlib.closing to ensure the close method of the stream object
            # will be called automatically at the end of the with statement's
            # scope.
            # with closing(stream) as managed_stream:
            # Push out the stream's content in chunks
            while True:
                # data = managed_stream.read(CHUNK_SIZE)
                data = stream
                self.wfile.write(self._html(data))

                # If there's no more data to read, stop streaming
                if not data:
                    break

            # Ensure any buffered output has been transmitted and close the
            # stream
            self.wfile.flush()

            print("Streaming completed.")
        else:
            # The stream passed in is empty
            self.wfile.write(b"0\r\n\r\n")
            print("Nothing to stream.")


def wait_for_request(host, port, token):
    # Create and configure the HTTP server instance
    handler = ChunkedHTTPRequestHandler
    handler.verification_token = token
    server = ThreadedHTTPServer((host, port),
                                handler)
    print("Starting server, use <Ctrl-C> to stop...")
    print(u"Open {0}://{1}:{2} in a web browser.".format(PROTOCOL,
                                                         host,
                                                         port,
                                                         ))

    try:
        # Listen for requests indefinitely
        server.handle_request()

    except KeyboardInterrupt:
        # A request to terminate has been received, stop the server
        print("\nShutting down...")
        server.socket.close()
