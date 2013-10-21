# -*- coding: utf-8 -*-

import time
import threading
import socket
import random

from ws4py.websocket import *

class JoystickMonitor(threading.Thread):
    def __init__(self, websocket, frequency=1.0):
        """
        Runs at a periodic interval specified by
        `frequency` by sending an unsolicitated pong
        message to the connected peer.

        If the message fails to be sent and a socket
        error is raised, we close the websocket
        socket automatically, triggering the `closed`
        handler.
        """
        threading.Thread.__init__(self)
        self.websocket = websocket
        self.frequency = frequency

    def __enter__(self):
        if self.frequency:
            self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            time.sleep(self.frequency)
            if self.websocket.terminated:
                break

            try:
                msg = str(random.randint(0, 10000))
                self.websocket.send(msg)
            except socket.error:
                break

class JoystickWebSocket(WebSocket):

    def run(self):
        """
        Performs the operation of reading from the underlying
        connection in order to feed the stream of bytes.

        We start with a small size of two bytes to be read
        from the connection so that we can quickly parse an
        incoming frame header. Then the stream indicates
        whatever size must be read from the connection since
        it knows the frame payload length.

        Note that we perform some automatic opererations:

        * On a closing message, we respond with a closing
          message and finally close the connection
        * We respond to pings with pong messages.
        * Whenever an error is raised by the stream parsing,
          we initiate the closing of the connection with the
          appropiate error code.

        This method is blocking and should likely be run
        in a thread.
        """
        self.sock.setblocking(True)
        #j = JoystickMonitor(self, frequency=1)
        #j.run()
        with Heartbeat(self, frequency=self.heartbeat_freq):
            s = self.stream

            try:
                self.opened()
                while not self.terminated:
                    #self.move()
                    if not self.once():
                        break
            finally:
                self.terminate()

    def received_message(self, message):
        """
        Automatically sends back the provided ``message`` to
        its originating endpoint.
        """
        self.send(message.data, message.is_binary)

    def move(self):
        #self.send('hello')
        num = random.randint(0, 5)
        #self.send(str(num))
        if (num == 2):
            self.send(str(num))


