import unittest
import logging
import client as AC


class socketMock:
    @staticmethod
    def connect_it():
        return True

    def __init__(self, *args):
        pass

    def connect(self, *args):
        return True


class SocketExceptionMock(socketMock):
    def connect(self, *args):
        raise Exception('something went wrong')


class LogMock:
    def info(self, msg):
        self.info_msg = msg

    def critical(self, msg):
        self.critical_msg = str(msg)


class TestProcessor(unittest.TestCase):
    def test_create_socket_connection(self):
        import socket
        socket.socket = socketMock
        log = LogMock()

        client = AC.Client('127.0.0.1', 1000, log, 'output', 'input', 1000)
        client.create_socket_connection()
        self.assertEquals(log.info_msg,
                          'socket connected to 127.0.0.1:1000')

    def test_create_socket_connection_exception(self):
        import socket
        socket.socket = SocketExceptionMock
        log = LogMock()

        client = AC.Client('127.0.0.1', 1000, log, 'output', 'input', 1000)
        client.create_socket_connection()
        self.assertEquals(log.critical_msg, 'something went wrong')

    def test_run(self):
        log = logging.getLogger('test')
        client = AC.Client('127.0.0.1', 1000, log, 'output', 'input', 1000)
        client.create_socket_connection = socketMock.connect_it
        self.assertRaises(IOError, client.run)

    def test_no_args_exception(self):
        self.assertRaises(SystemExit, AC.main)
