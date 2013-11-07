
import argparse
import websocket
import thread
import time
import signal, sys
from SimpleWebSocketServer import SimpleWebSocketServer

import theapipantilt.drivers as drivers
from theapipantilt.ws_server import SimpleChat


PWM_FREQUENCY = 50    # Hz
PWM_PULSE_INCREMENT_US = 5
PAN_PWM_PIN = 23
TILT_PWM_PIN = 24

def on_message(ws, message):
    servoControl.setVector(message)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Pan and Tilt')
    parser.add_argument('--host', default='192.168.0.145')
    parser.add_argument('-d', '--driver', default='rpiodriver')
    parser.add_argument('-p', '--port', default=8000, type=int)
    parser.add_argument("-P", "--invertpan", help="invert pan",
                    action="store_true")
    parser.add_argument("-T", "--inverttilt", help="invert tilt",
                    action="store_true")
    parser.add_argument("-S", "--server", help="Run the websocket server too",
                    action="store_true")

    args = parser.parse_args()

    servoControl= drivers.Drivers().getDriver(args, PWM_FREQUENCY, PWM_PULSE_INCREMENT_US)

    if (args.invertpan):
        servoControl.setInvertPan(args.invertpan)

    if (args.inverttilt):
        servoControl.setInvertTilt(args.inverttilt)


    # Initialise the pan & tilt mechanisms
    # todo configuration for pulse widths (& angles)
    if ('cube' == args.driver):
        servoControl.initPanServo( PAN_PWM_PIN, -60, 0, 60)
        servoControl.initTiltServo( TILT_PWM_PIN, -45, 0, 45)
    else:
        servoControl.initPanServo( PAN_PWM_PIN, 800, 1500, 2350)
        servoControl.initTiltServo( TILT_PWM_PIN, 900, 1300, 1850)

    # Websocket server
    if (args.server):
        ws_server = SimpleWebSocketServer(args.host, args.port, SimpleChat)
        # In a thread
        thread.start_new_thread(ws_server.serveforever, ())


    # Websocket client
    ws = websocket.WebSocketApp('ws://' + str(args.host) + ':' + str(args.port) + '/ws',
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)

    # Run the client in a thread
    thread.start_new_thread( ws.run_forever, ())

    while 1:
        time.sleep(0.05)
        servoControl.move()
        pass

