import unittest
import logging

from client import Client

from socket import socket


class Mock:
    def connect(self):
        pass


socket = Mock


class TestProcessor(unittest.TestCase):
    def test_create_socket_connection(self):
        mock_socket = Mock()
        mock_socket.socket = Mock()

        log = logging.getLogger('test')

        client = Client('127.0.0.1', 1000, log, 'output', 'input', 1000)
        client.create_socket_connection()

        self.assertEquals(True, True)
