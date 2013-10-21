# -*- coding: utf-8 -*-

from ws4py.server.geventserver import *


class WSGIMotorServer(WSGIServer):


    def __init__(self, *args, **kwargs):
        """
        WSGI server that adds motor movement

        Other than that, the server is the same
        as its :class:`ws4py.server.geventserver`
        base.
        """
        WSGIServer.__init__(self, *args, **kwargs)
        self.pool = GEventWebSocketPool()

        print "in WSGIMotorServer"

