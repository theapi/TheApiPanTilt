# -*- coding: utf-8 -*-

import os

from ws4py.server.geventserver import WebSocketWSGIHandler, WSGIServer
from ws4py.server.geventserver import WebSocketWSGIApplication
from ws4py.websocket import EchoWebSocket

class BroadcastWebSocket(EchoWebSocket):
    def opened(self):
        app = self.environ['ws4py.app']
        app.clients.append(self)

    def received_message(self, m):
        # self.clients is set from within the server
        # and holds the list of all connected servers
        # we can dispatch to
        app = self.environ['ws4py.app']
        for client in app.clients:
            client.send(m)

    def closed(self, code, reason="A client left the room without a proper explanation."):
        app = self.environ.pop('ws4py.app')
        if self in app.clients:
            app.clients.remove(self)
            for client in app.clients:
                try:
                    client.send(reason)
                except:
                    pass


class EchoWebSocketApplication(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ws = WebSocketWSGIApplication(handler_cls=BroadcastWebSocket)

        self.staticDir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

        #static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
        #f = open('/home/peterc/repos/picam/picam/static/js/virtualjoystick.js', 'r')
        #print f.read()

        # keep track of connected websocket clients
        # so that we can brodcasts messages sent by one
        # to all of them.
        self.clients = []

    def __call__(self, environ, start_response):
        """
        Good ol' WSGI application. This is a simple demo
        so I tried to stay away from dependencies.
        """


        if environ['PATH_INFO'] == '/favicon.ico':
            return self.favicon(environ, start_response)

        if environ['PATH_INFO'] == '/ws':
            environ['ws4py.app'] = self
            return self.ws(environ, start_response)

        if environ['PATH_INFO'] == '/css/main.css':
            return self.css(environ, start_response)

        if environ['PATH_INFO'] == '/js/virtualjoystick.js':
            return self.js(environ, start_response)

        return self.webapp(environ, start_response)

    def favicon(self, environ, start_response):
        """
        Don't care about favicon, let's send nothing.
        """
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return ""

    def css(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)

        f = open(self.staticDir + '/css/main.css', 'r')
        css = f.read()
        f.close()
        return css

    def js(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)

        f = open(self.staticDir + '/js/virtualjoystick.js', 'r')
        js = f.read()
        f.close()
        return js

    def webapp(self, environ, start_response):
        """
        Our main webapp that'll display the chat form
        """
        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        start_response(status, headers)

        return """<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
 <link rel="stylesheet" href="css/main.css" />

      <script type='application/javascript' src='https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js'></script>
      <script type='application/javascript'>
        $(document).ready(function() {



          websocket = 'ws://%(host)s:%(port)s/ws';
          if (window.WebSocket) {
            ws = new WebSocket(websocket);
          }
          else if (window.MozWebSocket) {
            ws = MozWebSocket(websocket);
          }
          else {
            console.log('WebSocket Not Supported');
            return;
          }

          window.onbeforeunload = function(e) {
            $('#wsresponse').val('Bye bye...');
            ws.close(1000, 'Bye');

            if(!e) e = window.event;
            e.stopPropagation();
            e.preventDefault();
          };
          ws.onmessage = function (evt) {
             $('#wsresponse').val(evt.data);
          };
          ws.onopen = function() {
             ws.send("0,0");
          };
          ws.onclose = function(evt) {
             $('#wsresponse').val('Connection closed by server: ' + evt.code + ' "' + evt.reason);
          };


        });
      </script>

    </head>
    <body>

        <div id="container"></div>
        <div id="info">

    <form action='#' id='chatform' method='get'>
      <label for='send'>Send: </label><input type='text' id='send' />
      <label for='wsresponse'>Socket response: </label><input type='text' id='wsresponse' />
      </form>

            <span id="result"></span>
        </div>
        <script src="/js/virtualjoystick.js"></script>
        <script>
            console.log("touchscreen is", VirtualJoystick.touchScreenAvailable() ? "available" : "not available");
            var joystick    = new VirtualJoystick({
                container   : document.getElementById('container'),
                mouseSupport    : true
            });
            setInterval(function(){
                $msg = joystick.deltaX() + ',' + joystick.deltaY();
                                if ($('#send').val() != $msg) {
                    $('#send').val($msg);
                                        ws.send($msg);
                }

                var outputEl    = document.getElementById('result');
                outputEl.innerHTML  = '<b>Result:</b> '
                    + ' dx:'+joystick.deltaX()
                    + ' dy:'+joystick.deltaY()
                    + (joystick.right() ? ' right'  : '')
                    + (joystick.up()    ? ' up'     : '')
                    + (joystick.left()  ? ' left'   : '')
                    + (joystick.down()  ? ' down'   : '');

            }, 1/30 * 1000);
        </script>
    </body>
</html>
        """ % {'host': self.host, 'port': self.port}


