# -*- coding: utf-8 -*-

# sudo apt-get install python-gevent

from gevent import monkey; monkey.patch_all()

import argparse
import os

import gevent
import gevent.pywsgi

from ws4py.server.geventserver import WSGIServer
from picam.joystick import JoystickWebSocketApplication

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Joystick gevent Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9001, type=int)
    args = parser.parse_args()

    server = WSGIServer((args.host, args.port), JoystickWebSocketApplication(args.host, args.port))
    server.serve_forever()
