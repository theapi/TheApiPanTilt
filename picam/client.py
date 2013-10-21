# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient

class JoystickClient(WebSocketClient):

    def __init__(self, url, protocols=None, extensions=None, heartbeat_freq=None,
                 ssl_options=None, headers=None):
        WebSocketClient.__init__(self, url, protocols, extensions, heartbeat_freq,
                                     ssl_options, headers=headers)
        self.panServo = None
        self.tiltServo = None


    def closed(self, code, reason):
        print(("Closed down", code, reason))

    def received_message(self, m):
        print("WS: " + str(m))
        vector = command.split(',')
        x = int( vector[0].strip() )
        y = int( vector[1].strip() )

        # Register the input
        self.panServo.joystickInput( x )
        self.tiltServo.joystickInput( y )

        if len(m) == 175:
            self.close(reason='Bye bye')

    def addPanServo(self, servo):
        self.panServo = servo

    def addTiltServo(self, servo):
        self.tiltServo = servo

if __name__ == '__main__':
    try:
        ws = JoystickClient('ws://localhost:9000/ws', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
