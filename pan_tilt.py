# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all(select=False)

import argparse
import time
import gevent
from ws4py.client.geventclient import WebSocketClient

from picam.servo import *

PWM_FREQUENCY = 50    # Hz
PWM_PULSE_INCREMENT_US = 5
PAN_PWM_PIN = 23
TILT_PWM_PIN = 24



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Pan and Tilt')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9001, type=int)
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


    # Create Servo instances to control the servos
    panServo = servoControl.getPanServo( PAN_PWM_PIN,
        minAnglePulseWidthPair=( 50.0, 2100 ),
        midAnglePulseWidthPair=( 90.0, 1300 ),
        maxAnglePulseWidthPair=( 130.0, 800.0 ) )

    tiltServo = servoControl.getTiltServo( TILT_PWM_PIN,
        minAnglePulseWidthPair=( 45.0, 2100 ),
        midAnglePulseWidthPair=( 90.0, 1800 ),
        maxAnglePulseWidthPair=( 130.0, 800.0 ) )


    ws = WebSocketClient('ws://' + str(args.host) + ':' + str(args.port) + '/ws', protocols=['http-only', 'chat'])
    ws.connect()

    ws.send("Hello world")
    print((ws.receive(),))

    ws.send("Hello world again")
    print((ws.receive(),))

    def incoming():
        while True:
            m = ws.receive()
            if m is not None:
                m = str(m)
                print "WS: " + m
                servoControl.setVector(m)

                if len(m) == 35:
                    ws.close()
                    break
            else:
                break
        print(("Connection closed!",))

    def joystick():
        while True:
            time.sleep(0.01)
            # Move if joystick is not centered
            #x = panServo.getLastJoystickInput()
            #y = tiltServo.getLastJoystickInput()

            servoControl.move()

            #if (x != 0):
            #    panServo.movePulseIncrement( x )
            #if (y != 0):
            #    tiltServo.movePulseIncrement( y )


    greenlets = [
        gevent.spawn(incoming),
        gevent.spawn(joystick),
    ]
    gevent.joinall(greenlets)
