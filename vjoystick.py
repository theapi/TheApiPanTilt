# -*- coding: utf-8 -*-

# sudo apt-get install python-gevent

from gevent import monkey; monkey.patch_all()

import argparse
import os

import gevent
import gevent.pywsgi

from ws4py.server.geventserver import WSGIServer

from picam.echo import EchoWebSocketApplication

if __name__ == '__main__':
    #from ws4py import configure_logger
    #configure_logger()

    parser = argparse.ArgumentParser(description='Echo gevent Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    args = parser.parse_args()

    server = WSGIServer((args.host, args.port), EchoWebSocketApplication(args.host, args.port))
    server.serve_forever()
