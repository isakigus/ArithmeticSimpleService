import unittest

from common import get_log
from algebra import ArithmeticOperator, ArithmeticPool


class ArithmeticOperatorValidationTest(unittest.TestCase):
    def validate(self, operation):
        return ArithmeticOperator.validate_operation_string(operation)

    def test_validate_operation_string(self):
        self.assertEqual('valid', self.validate("3 + 4 * 2 + 4 / 5"))

    def test_validate_operation_string_not_well_spaced(self):
        self.assertEqual('valid', self.validate("3 + 4 * 2 + 4 /    5"))

    def test_validate_operation_string_no_valid_operator(self):
        self.assertNotEqual('valid', self.validate("3 + 4 * ? + 4 / 5"))

    def test_validate_operation_string_valid_first_element1(self):
        self.assertEqual('valid', self.validate("- 3 + 4 * 4 / 5"))

    def test_validate_operation_string_valid_first_element2(self):
        self.assertEqual('valid', self.validate(" - 3 + 4  + 4 / 5"))

    def test_validate_operation_string_no_valid_first_element1(self):
        self.assertNotEqual('valid', self.validate("+ 3 / 4 * 5"))

    def test_validate_operation_string_no_valid_first_element2(self):
        self.assertNotEqual('valid', self.validate("zz 3 / 4 * 5"))

    def test_validate_operation_string_no_valid_first_last_element1(self):
        self.assertNotEqual('valid', self.validate("3 / 4 * 5 +"))

    def test_validate_operation_string_no_valid_first_last_element2(self):
        self.assertNotEqual('valid', self.validate("3 / 4 * 5 sdr "))

    def test_validate_operation_string_no_valid_operator2(self):
        self.assertNotEqual('valid', self.validate("3 / 4 z* 5"))


class ArithmeticOperatorOperationTest(unittest.TestCase):
    def test_operate_simple_addition(self):
        self.assertEqual(ArithmeticOperator.operate("3 + 4"), 7.0)

    def test_operate_simple_addition2(self):
        self.assertEqual(ArithmeticOperator.operate("3 + 4 - 2"), 5.0)

    def test_operate_simple_multiplication(self):
        self.assertEqual(ArithmeticOperator.operate("3 * 4 * 2"), 24.0)

    def test_operate_simple_multiplication_and_division(self):
        self.assertEqual(ArithmeticOperator.operate("12 / 4 * 2"), 6.0)

    def test_operate_division(self):
        self.assertEqual(ArithmeticOperator.operate("12 / 5 * 2"), 4.8)

    def test_operate_complete_expression1(self):
        self.assertEqual(ArithmeticOperator.operate("12 / 5 * 2 + 12 - 3 * 2"),
                         10.8)

    def test_operate_complete_expression2(self):
        self.assertEqual(ArithmeticOperator.operate("2 * 5 + 20 - 3 * 2"), 24.0)

    def test_operate_complete_expression3(self):
        self.assertEqual(ArithmeticOperator.operate("-2 * 5 + 20 - 3 * 2"), 4.0)

    def test_operate_complete_expression4(self):
        self.assertEqual(ArithmeticOperator.operate(" -2 * 5 + 20 - 3 * 2"),
                         4.0)

    def test_operate_complete_expression5(self):
        self.assertEqual(ArithmeticOperator.operate(" - 2 * 5 + 20 - 3 * 2"),
                         4.0)

    def test_operate_complete_expression6(self):
        self.assertEqual(
            ArithmeticOperator.validate_and_operate(" - 2 * 5 + 20 - 3 * 2"),
            4.0)

    def test_operate_and_validate_complete_expression1(self):
        self.assertEqual(
            ArithmeticOperator.validate_and_operate(" - 2 * 5 + 20 - 3 * 2"),
            4.0)

    def test_operate_and_validate_complete_expression2(self):
        self.assertEqual(
            ArithmeticOperator.validate_and_operate("e 2 * 5 + 20 - 3 * 2"),
            'first element is not valid')

    def test_operate_and_validate_complete_expression3(self):
        self.assertEqual(
            ArithmeticOperator.validate_and_operate("-- 2 * 5 + 20 - 3 * 2"),
            'two consecutive operators found, wrong syntax')

    def test_operate_and_validate_complete_expression4(self):
        self.assertEqual(
            ArithmeticOperator.validate_and_operate("-2 * + 5 + 20 - 3 * 2"),
            'two consecutive operators found, wrong syntax')


class PipeMock:
    def __init__(self, msg_to_send):
        self.msg_to_send = msg_to_send

    def poll(self):
        return True

    def recv(self):
        return self.msg_to_send


class QueueMock:
    def __init__(self, test_obj, expected, ref_obj):
        self.test = test_obj
        self.expected = expected
        self.ref_obj = ref_obj

    def put(self, data):
        self.test.assertEqual(data, self.expected)
        self.ref_obj.number_children = 0


class TestPassed(Exception):
    pass


class LogMock:
    msg_number = 1

    def __init__(self, msg_expected, test_obj, msg_number):
        self.msg_expected = msg_expected
        self.test = test_obj
        self.msg_number = msg_number

    def debug(self, msg):
        if LogMock.msg_number == self.msg_number:
            self.test.assertEqual(msg, self.msg_expected)
            raise TestPassed()
        LogMock.msg_number += 1


class MockConn:
    def __init__(self, test_obj, ro_recv):
        self.test = test_obj
        self.data = None
        self.to_recv = ro_recv

    def recv(self):
        return self.to_recv

    def send(self, data):
        self.data = data


class MockProcess:
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        print ':)'


class OutputQueueMock:
    def get(self):
        return 'data'


class TestArithmeticPool(unittest.TestCase):
    def test_listener_loop(self):
        child_conn = PipeMock('test')
        log = get_log('test', True)
        test_process = None
        test_pool = ArithmeticPool(2, log)

        q = QueueMock(self, 'test', test_pool)
        ps = [(test_process, child_conn)]

        test_pool.listener_loop(ps, q)

    def test_listener_loop2(self):
        test_process = 'test_process'
        msg_expected = 'process %s stopping , left running:%s' % (
            test_process, 0)

        log = LogMock(msg_expected, self, 2)
        child_conn = PipeMock(ArithmeticPool.TERMINATING_MSG)

        test_pool = ArithmeticPool(1, log)

        q = QueueMock(self, ArithmeticPool.TERMINATING_MSG, test_pool)
        ps = [(test_process, child_conn)]

        try:
            test_pool.listener_loop(ps, q)
        except TestPassed:
            self.assertTrue(True)

    def test_job1(self):
        log = get_log('test', True)
        test_pool = ArithmeticPool(2, log)

        conn = MockConn(self, (ArithmeticPool.STOP_PILL, 0))

        test_pool.job(0, conn)

        self.assertEqual(conn.data, ArithmeticPool.TERMINATING_MSG)

    def test_job2(self):
        msg_expected = ("process[%s] response, input_line[%s]:"
                        " %s = %s ") % (0, 0, '2+2', '4.0')

        log = LogMock(msg_expected, self, 1)

        test_pool = ArithmeticPool(2, log)

        conn = MockConn(self, ('2+2', 0))

        try:
            test_pool.job(0, conn)
        except TestPassed:
            self.assertTrue(True)

    def test_job3(self):
        msg_expected = ("process[%s] response, input_line[%s]:"
                        " %s = %s ") % (0, 0, '2+2', '4.0')

        log = LogMock(msg_expected, self, 1)

        test_pool = ArithmeticPool(2, log)
        test_pool.validate_operations = False

        conn = MockConn(self, ('2+2', 0))

        try:
            test_pool.job(0, conn)
        except TestPassed:
            self.assertTrue(True)

    def test_job4(self):
        msg_expected = ('error[0] response, input_line[0]: 2+A = could not '
                        'convert string to float: A ')

        log = LogMock(msg_expected, self, 1)

        test_pool = ArithmeticPool(2, log)
        test_pool.validate_operations = False

        conn = MockConn(self, ('2+A', 0))

        try:
            test_pool.job(0, conn)
        except TestPassed:
            self.assertTrue(True)

    def test_pool_processor(self):
        log = get_log('test', True)
        test_pool = ArithmeticPool(2, log)

        data = ['2+2']

        import multiprocessing

        multiprocessing.Process = MockProcess
        multiprocessing.Queue = OutputQueueMock

        result = test_pool.pool_processor(data)

        self.assertEquals(['data'], result)
