#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import random
import os
import time


import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

from ServoControl import *

PWM_FREQUENCY = 50    # Hz
PWM_PULSE_INCREMENT_US = 5
PAN_PWM_PIN = 23
TILT_PWM_PIN = 24

servoControl = ServoControl(PWM_FREQUENCY, PWM_PULSE_INCREMENT_US)


# Create Servo instances to control the servos
panServo = servoControl.getServo( PAN_PWM_PIN,
    minAnglePulseWidthPair=( 50.0, 2100 ),
    midAnglePulseWidthPair=( 90.0, 1300 ),
    maxAnglePulseWidthPair=( 130.0, 800.0 ) )

tiltServo = servoControl.getServo( TILT_PWM_PIN,
    minAnglePulseWidthPair=( 45.0, 2100 ),
    midAnglePulseWidthPair=( 90.0, 1800 ),
    maxAnglePulseWidthPair=( 135.0, 900.0 ) )



def positionCam():
    x = panServo.getLastJoystickInput()
    print 'poscam x: ' + str(x)
    #if x != 0:
    panServo.movePulseIncrement( x )


    y = tiltServo.getLastJoystickInput()
    print 'poscam y: ' + str(y)
    #if y != 0:
    tiltServo.movePulseIncrement( y )

class ChatWebSocketHandler(WebSocket):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', m)
        # Process pixel data
        command = str(m)
        print "WS: " + command
        vector = command.split(',')
        x = int( vector[0].strip() )
        y = int( vector[1].strip() )

        # Register the input
        panServo.joystickInput( x )
        tiltServo.joystickInput( y )


        # TMP until I find a way to add a loop with the websocket...
        positionCam()
        time.sleep( 0.001 )

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        return """<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
 <link rel="stylesheet" href="css/main.css" />

      <script type='application/javascript' src='https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js'></script>
      <script type='application/javascript'>
        $(document).ready(function() {



          websocket = '%(scheme)s://%(host)s:%(port)s/ws';
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
    """ % {'username': self.host, 'host': self.host, 'port': self.port, 'scheme': self.scheme}

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))



if __name__ == '__main__':
    import logging
    from ws4py import configure_logger
    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl', action='store_true')
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    if args.ssl:
        cherrypy.config.update({'server.ssl_certificate': './server.crt',
                                'server.ssl_private_key': './server.key'})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port, args.ssl), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': ChatWebSocketHandler
            },
        '/css': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'css'
            },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
            }
        }
    )





