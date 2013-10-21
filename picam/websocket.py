# -*- coding: utf-8 -*-

from ws4py.websocket import WebSocket

class JoystickWebSocket(WebSocket):

    def received_message(self, message):
        """
        Automatically sends back the provided ``message`` to
        its originating endpoint.
        """
        self.send(message.data, message.is_binary)

