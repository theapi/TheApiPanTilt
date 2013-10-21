# -*- coding: utf-8 -*-

# sudo apt-get install python-gevent

from gevent import monkey; monkey.patch_all()

import argparse
import os

import gevent
import gevent.pywsgi

#from ws4py.server.geventserver import WSGIServer
from picam.server import WSGIMotorServer

from picam.joystick import JoystickWebSocketApplication

if __name__ == '__main__':
    #from ws4py import configure_logger
    #configure_logger()

    parser = argparse.ArgumentParser(description='Echo gevent Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9001, type=int)
    args = parser.parse_args()

    server = WSGIMotorServer((args.host, args.port), JoystickWebSocketApplication(args.host, args.port))
    server.serve_forever()
