#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import os
import requests

class S(BaseHTTPRequestHandler):
    def _set_response(self, length):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', length)
        self.end_headers()
    
    def _get_body(self):
        data = ''
        if self.headers['Content-Length']:
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data = data.decode('utf-8')
        return data

    def _process_request(self):
        data = self._get_body()
        r = {}
        r['method']=str(self.command)
        r['path']=str(self.path)
        r['headers']=dict(self.headers)
        r['body']=data
        envs=[]
        for k, v in os.environ.items():
            envs.append(k+"='"+v+"'")
        r['os_envs']=sorted(envs)
        logging.info("\n> Method: %s\n> Version: %s\n> Path: %s\n> Headers:\n%s> Body:\n%s\n",
                str(self.command), str(self.request_version), str(self.path), str(self.headers), data)
        return r

    def _remove_prefix(self):
        text = str(self.path)
        prefix = '/proxy-to/'
        return text[text.startswith(prefix) and len(prefix):]

    def _forward_trace_headers(self):
        headers = {}
        for request_header in dict(self.headers):
            if (request_header.lower() in ['x-request-id', 'x-b3-traceid', 'x-b3-spanid', 'x-b3-parentspanid', 'x-b3-sampled', 'x-b3-flags', 'b3']) or (request_header.lower().startswith('x-ifood-')):
                headers[request_header] = self.headers[request_header]
        logging.info('trace headers => ' + str(headers))
        return headers

    def _filter_headers(self, headers_names):
        headers = {}
        for request_header in dict(self.headers):
            if (request_header.lower() in headers_names):
                headers[request_header] = self.headers[request_header]
        logging.info('forward only these headers => ' + str(headers))
        return headers

    def _forward_headers(self):
        headers = dict(self.headers) if (os.getenv('FORWARD_ALL_HEADERS', 'true') == 'true') else dict({})
        headers = self._forward_trace_headers() if (os.getenv('FORWARD_TRACE_HEADERS', 'true') == 'true') else headers
        if 'x-req-forward-only-these-headers' in  [x.lower() for x in list(dict(self.headers).keys())]:
            headers_names = [ v for k, v in dict(self.headers).items() if k.lower() == 'x-req-forward-only-these-headers'][0].split(",")
            headers_names = [ n.strip().lower() for n in headers_names ]
            headers = self._filter_headers(headers_names)
        return headers

    def _proxy_to(self):
        URL = self._remove_prefix()
        headers = self._forward_headers()
        if 'Content-Length' in headers.keys():
            headers.pop('Content-Length', None)
            logging.warning('Payload will not be proxyed')
        r = requests.get(url = URL, headers = headers)
        self.send_response(r.status_code)
        for h in dict(r.headers):
            self.send_header(h, str(r.headers[h]))
        self.end_headers()
        self.wfile.write(r.text.encode('utf-8'))

    def do_GET(self):
        if str(self.path).startswith('/proxy-to/'):
            self._process_request()
            self._proxy_to()
        else:
            r = json.dumps(self._process_request(), indent=2).encode('utf-8')
            self._set_response(len(r))
            self.wfile.write(r)

    def do_HEAD(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)

    def do_POST(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)

    def do_PUT(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)

    def do_DELETE(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)

    def do_CONNECT(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)

    def do_OPTIONS(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)

    def do_TRACE(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)

    def do_PATCH(self):
        r = json.dumps(self._process_request(), indent=2).encode('utf-8')
        self._set_response(len(r))
        self.wfile.write(r)


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
