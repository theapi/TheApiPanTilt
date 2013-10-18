#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import random
import os
import time
import RPIO
import RPIO.PWM

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

PWM_FREQUENCY = 50    # Hz

PWM_DMA_CHANNEL = 0
PWM_SUBCYLCLE_TIME_US = 1000/PWM_FREQUENCY * 1000
PWM_PULSE_INCREMENT_US = 5

PAN_PWM_PIN = 23
TILT_PWM_PIN = 24

ABSOLUTE_MIN_PULSE_WIDTH_US = 500
ABSOLUTE_MAX_PULSE_WIDTH_US = 2500

#-------------------------------------------------------------------------------
class ServoPWM:

    #---------------------------------------------------------------------------
    def __init__( self, pwmPin, minAnglePulseWidthPair,
        midAnglePulseWidthPair, maxAnglePulseWidthPair ):

        # Check that the given angles are valid
        assert( minAnglePulseWidthPair[ 0 ] >= 0 )
        assert( midAnglePulseWidthPair[ 0 ] > minAnglePulseWidthPair[ 0 ] )
        assert( midAnglePulseWidthPair[ 0 ] < maxAnglePulseWidthPair[ 0 ] )
        assert( maxAnglePulseWidthPair[ 0 ] <= 180 )

        self.pwmPin = pwmPin
        self.minAnglePulseWidthPair = minAnglePulseWidthPair
        self.midAnglePulseWidthPair = midAnglePulseWidthPair
        self.maxAnglePulseWidthPair = maxAnglePulseWidthPair
        self.lastPulseWidthSet = None

    #---------------------------------------------------------------------------
    def setCommand( self, command ):

        # Work out whether the command is an angle, or a pulse width
        if command >= ABSOLUTE_MIN_PULSE_WIDTH_US:
            self.setPulseWidth( command )
        else:
            self.setAngle( command )

    #---------------------------------------------------------------------------
    def setPulseWidth( self, pulseWidth ):

        # Constrain the pulse width
        if pulseWidth < ABSOLUTE_MIN_PULSE_WIDTH_US:
            pulseWidth = ABSOLUTE_MIN_PULSE_WIDTH_US
        if pulseWidth > ABSOLUTE_MAX_PULSE_WIDTH_US:
            pulseWidth = ABSOLUTE_MAX_PULSE_WIDTH_US

        # Ensure that the pulse width is an integer multiple of the smallest
        # possible pulse increment
        pulseIncrementUS = RPIO.PWM.get_pulse_incr_us()
        numPulsesNeeded = int( pulseWidth/pulseIncrementUS )
        pulseWidth = numPulsesNeeded * pulseIncrementUS

        if pulseWidth != self.lastPulseWidthSet:

            RPIO.PWM.add_channel_pulse( PWM_DMA_CHANNEL, self.pwmPin, 0, numPulsesNeeded )
            self.lastPulseWidthSet = pulseWidth

    #---------------------------------------------------------------------------
    def movePulseIncrement( self, pulseIncrement ):

        if self.lastPulseWidthSet is None:
            command = self.midAnglePulseWidthPair[ 1 ] + pulseIncrement
        else:
            command = self.lastPulseWidthSet + pulseIncrement

        # Stop it going too far for this servo's settings.
        if command < self.maxAnglePulseWidthPair[ 1 ]:
            command = self.maxAnglePulseWidthPair[ 1 ]
        elif command >self.minAnglePulseWidthPair[ 1 ]:
            command = self.minAnglePulseWidthPair[ 1 ]

        print command

        self.setPulseWidth( command )

    #---------------------------------------------------------------------------
    def setAngle( self, angle ):

        # Constrain the angle
        if angle < self.minAnglePulseWidthPair[ 0 ]:
            angle = self.minAnglePulseWidthPair[ 0 ]
        if angle > self.maxAnglePulseWidthPair[ 0 ]:
            angle = self.maxAnglePulseWidthPair[ 0 ]

        # Convert the angle to a pulse width using linear interpolation
        if angle < self.midAnglePulseWidthPair[ 0 ]:

            angleDiff = self.midAnglePulseWidthPair[ 0 ] - self.minAnglePulseWidthPair[ 0 ]
            startPulseWidth = self.minAnglePulseWidthPair[ 1 ]
            pulseWidthDiff = self.midAnglePulseWidthPair[ 1 ] - self.minAnglePulseWidthPair[ 1 ]

            interpolation = float( angle - self.minAnglePulseWidthPair[ 0 ] ) / angleDiff

            pulseWidth = startPulseWidth + interpolation*pulseWidthDiff

        else:

            angleDiff = self.maxAnglePulseWidthPair[ 0 ] - self.midAnglePulseWidthPair[ 0 ]
            startPulseWidth = self.midAnglePulseWidthPair[ 1 ]
            pulseWidthDiff = self.maxAnglePulseWidthPair[ 1 ] - self.midAnglePulseWidthPair[ 1 ]

            interpolation = float( angle - self.midAnglePulseWidthPair[ 0 ] ) / angleDiff

            pulseWidth = startPulseWidth + interpolation*pulseWidthDiff

        print "Converted angle {0} to pulse width {1}".format( angle, pulseWidth )

        # Now set the pulse width
        self.setPulseWidth( pulseWidth )


class ChatWebSocketHandler(WebSocket):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', m)
        # Process pixel data here...

        # Move camera...
        panServoPWM.movePulseIncrement( 5 )
        time.sleep( 0.05 )

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

    #-------------------------------------------------------------------------------
    # Create ServoPWM instances to control the servos
    panServoPWM = ServoPWM( PAN_PWM_PIN,
        minAnglePulseWidthPair=( 45.0, 1850 ),
        midAnglePulseWidthPair=( 90.0, 1100 ),
        maxAnglePulseWidthPair=( 180.0, 500.0 ) )
    tiltServoPWM = ServoPWM( TILT_PWM_PIN,
        minAnglePulseWidthPair=( 45.0, 2100 ),
        midAnglePulseWidthPair=( 90.0, 1700 ),
        maxAnglePulseWidthPair=( 135.0, 1100.0 ) )

    # Setup RPIO, and prepare for PWM signals
    RPIO.setmode( RPIO.BCM )

    RPIO.PWM.setup( pulse_incr_us=PWM_PULSE_INCREMENT_US )
    RPIO.PWM.init_channel( PWM_DMA_CHANNEL, PWM_SUBCYLCLE_TIME_US )


