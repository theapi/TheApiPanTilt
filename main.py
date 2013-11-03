
import argparse
import websocket
import thread
import time
import imp

try:
    imp.find_module('RPIO')
    from theapipantilt.drivers.rpiodriver import RPIOServoControl as ServoControl
except ImportError:
    from theapipantilt.drivers.dummydriver import DummyServoControl as ServoControl



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
    parser.add_argument('-p', '--port', default=8000, type=int)
    parser.add_argument("-P", "--invertpan", help="invert pan",
                    action="store_true")
    parser.add_argument("-T", "--inverttilt", help="invert tilt",
                    action="store_true")

    args = parser.parse_args()

    servoControl = ServoControl(PWM_FREQUENCY, PWM_PULSE_INCREMENT_US)

    if (args.invertpan):
        servoControl.setInvertPan(args.invertpan)

    if (args.inverttilt):
        servoControl.setInvertTilt(args.inverttilt)


    # Initialise the pan & tilt mechanisms
    servoControl.initPanServo( PAN_PWM_PIN, 800, 1500, 2350)
    servoControl.initTiltServo( TILT_PWM_PIN, 900, 1300, 1850)

    ws = websocket.WebSocketApp('ws://' + str(args.host) + ':' + str(args.port) + '/ws',
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)

    # Run the client in a thread
    thread.start_new_thread( ws.run_forever, ())

    while 1:
        time.sleep(0.01)
        servoControl.move()
        pass

