import logging
import unittest

from common import END_SEQUENCE
from service import Processor, ArithmeticService


class Mock:
    TEST_MESSAGE = 'x'
    msgs_counter = 0
    TEST_MESSAGE_LOOP = 3

    def recv(self, block):
        Mock.msgs_counter += 1

        if Mock.msgs_counter > Mock.TEST_MESSAGE_LOOP:
            Mock.msgs_counter = 0
            return END_SEQUENCE

        return Mock.TEST_MESSAGE

    def send(self, data):
        self.data_sent = Mock.TEST_MESSAGE * Mock.TEST_MESSAGE_LOOP

    def close(self):
        return 'socket closed'


class MockSocket(object):
    pass


class TestProcessor(unittest.TestCase):
    def test_get_data_from_socket(self):
        mock_socket = Mock()
        mock_socket.socket = Mock()

        log = logging.getLogger('test')

        processor = Processor(mock_socket, 1000, log, 1)
        processor.get_data_from_socket()

        self.assertEquals(''.join(processor.data),
                          Mock.TEST_MESSAGE * Mock.TEST_MESSAGE_LOOP)

    def test_send_response(self):
        mock_socket = Mock()
        mock_socket.socket = Mock()

        log = logging.getLogger('test')

        processor = Processor(mock_socket, 1000, log, 1)
        processor.do_job()

        self.assertEquals([mock_socket.data_sent], processor.data)


class TestArithmeticService(unittest.TestCase):
    def test_run_it(self):
        arithmetic_service = ArithmeticService(False, '0.0.0.0', 5555, 2, 1000,
                                               2)
        # arithmetic_service.run()
