import multiprocessing
import unittest


class ArithmeticOperatorValidationTest(unittest.TestCase):
    def validate(self, operation):
        return ArithmeticOperator.validate_operation_string(operation)

    def test_validate_opeartion_string(self):
        self.assertEqual('valid', self.validate("3 + 4 * 2 + 4 / 5"))

    def test_validate_opeartion_string_not_well_spaced(self):
        self.assertEqual('valid', self.validate("3 + 4 * 2 + 4 /    5"))

    def test_validate_opeartion_string_unvalid_operator(self):
        self.assertNotEqual('valid', self.validate("3 + 4 * ? + 4 / 5"))

    def test_validate_opeartion_string_valid_firts_element1(self):
        self.assertEqual('valid', self.validate("- 3 + 4 * 4 / 5"))

    def test_validate_opeartion_string_valid_firts_element2(self):
        self.assertEqual('valid', self.validate(" - 3 + 4  + 4 / 5"))

    def test_validate_opeartion_string_unvalid_firts_element1(self):
        self.assertNotEqual('valid', self.validate("+ 3 / 4 * 5"))

    def test_validate_opeartion_string_unvalid_firts_element2(self):
        self.assertNotEqual('valid', self.validate("zz 3 / 4 * 5"))

    def test_validate_opeartion_string_unvalid_firts_last_element1(self):
        self.assertNotEqual('valid', self.validate("3 / 4 * 5 +"))

    def test_validate_opeartion_string_unvalid_firts_last_element2(self):
        self.assertNotEqual('valid', self.validate("3 / 4 * 5 sdr "))

    def test_validate_opeartion_string_unvalid_operator2(self):
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
        self.assertEqual(ArithmeticOperator.operate("12 / 5 * 2 + 12 - 3 * 2"), 10.8)

    def test_operate_complete_expression2(self):
        self.assertEqual(ArithmeticOperator.operate("2 * 5 + 20 - 3 * 2"), 24.0)

    def test_operate_complete_expression3(self):
        self.assertEqual(ArithmeticOperator.operate("-2 * 5 + 20 - 3 * 2"), 4.0)

    def test_operate_complete_expression4(self):
        self.assertEqual(ArithmeticOperator.operate(" -2 * 5 + 20 - 3 * 2"), 4.0)

    def test_operate_complete_expression5(self):
        self.assertEqual(ArithmeticOperator.operate(" - 2 * 5 + 20 - 3 * 2"), 4.0)


class WrongOperatorFoundException(Exception):
    pass


class ArithmeticOperator:
    VALID = 'valid'
    VALID_CHARSET = '1234567890+-*/ '

    @staticmethod
    def validate_operation_string(operation_string):
        op = operation_string.strip()
        wrong_char_index = -1

        for idx, char in enumerate(operation_string):
            if char not in ArithmeticOperator.VALID_CHARSET:
                wrong_char_index = idx
                break

        if wrong_char_index > 0:
            return 'wrong char, at position %s, not in %s' % (wrong_char_index, ArithmeticOperator.VALID_CHARSET)

        if not op[-1].isdigit():
            return 'last element is not valid'

        if not op[0].isdigit() and op[0] != '-':
            return 'first element is not valid'

        return ArithmeticOperator.VALID

    @staticmethod
    def operate(operation_string):
        # first separation of assciative terms is needed
        data = operation_string.replace('-', '+-')
        aux, reduction = data.split('+'), []

        for mul in aux:
            # if multiplication group is empty, ignore it.
            mul = mul.strip()
            if not mul:
                continue

            # this add spaces between operators if there come without it.
            mul = mul.replace('/', '+/+')
            mul = ' '.join(mul.split('+'))
            mul = mul.replace('*', '+*+')
            mul = ' '.join(mul.split('+'))

            # removes spaces with negative sign to right convert it to float
            mul = mul.replace('- ', '-')
            # remove positive sign in first element
            mul = mul.lstrip('+')

            buff = mul.split()
            idx, total = 0, float(buff[0])

            # so we operate taking two by two elements
            while idx + 2 < len(buff):
                operator = buff[idx + 1]
                if operator == '*':
                    total *= float(buff[idx + 2])
                elif operator == '/':
                    total /= float(buff[idx + 2])
                else:
                    raise WrongOperatorFoundException
                idx += 2

            # and we do the addition of all elemnts once
            # the associative terms have been calculated.
            reduction.append(total)

        return sum(reduction)

    @staticmethod
    def validate_and_operate(operation_string):
        validation_msg = ArithmeticOperator.validate_operation_string(operation_string)

        if validation_msg == ArithmeticOperator.VALID:
            return ArithmeticOperator.operate(operation_string)
        else:
            return validation_msg


class ArithmecticPool:
    STOP_PILL = 'stop'
    TERMINATING_MSG = 'end'

    def __init__(self, no_childs, log, validate_operations=True):
        self.no_childs = no_childs
        self.log = log
        self.validate_operations = validate_operations

    def job(self, i, conn):
        while True:
            (msg, n) = conn.recv()
            # self.log.debug("process %s %s  - msgno %s" % (i, msg, n))

            if msg == ArithmecticPool.STOP_PILL:
                conn.send(ArithmecticPool.TERMINATING_MSG)
                self.log.debug("end sent %s" % i)
                break
            else:
                try:
                    if self.validate_operations:
                        result = ArithmeticOperator.validate_and_operate(msg)
                    else:
                        result = ArithmeticOperator.operate(msg)

                    return_msg = "process[%s] response, input_line[%s]: %s = %s " % (i, n, msg, result)
                    conn.send(return_msg)
                    self.log.debug(return_msg)

                except Exception as ex:
                    error_msg = "error[%s] response, input_line[%s]: %s = %s " % (i, n, msg, ex)
                    conn.send(error_msg)
                    self.log.debug(return_msg)

    def listener_loop(self, ps, q_out):

        while self.no_childs:
            for p in ps:
                if p[1].poll():
                    msg_in = p[1].recv()
                    self.log.debug(msg_in)
                    if msg_in.strip() == ArithmecticPool.TERMINATING_MSG:
                        self.no_childs -= 1
                        self.log.debug('process %s stopping , left running:%s' % (p[0], self.no_childs))
                    else:
                        q_out.put(msg_in)

    def pool_processor(self, operations_data):
        process_list, output_queue = [], multiprocessing.Queue()

        for i in range(self.no_childs):
            parent_conn, child_conn = multiprocessing.Pipe()
            p = multiprocessing.Process(target=self.job, args=(i, child_conn,))
            p.daemon = True
            process_list.append((p, parent_conn))

        listener = multiprocessing.Process(target=self.listener_loop,
                                           args=(process_list, output_queue,))
        listener.daemon = True
        listener.start()

        for process_tuple in process_list:
            process_tuple[0].start()

        idx = no_messages_sent = 0

        for msg in operations_data:
            idx = idx if idx != self.no_childs else 0
            process_list[idx][1].send((msg, no_messages_sent))
            no_messages_sent += 1
            """
            self.log.debug(
                'sending ... to process:%s total_msg_sent:%s / %s' % (idx, no_messages_sent, records_to_process))
            """
            idx += 1

        for process_tuple in process_list:
            process_tuple[1].send((ArithmecticPool.STOP_PILL, 0))
            self.log.debug('  -> stopping ... %s' % process_tuple[0])

        results = []

        while len(results) != no_messages_sent:
            element = output_queue.get()
            results.append(element)

        self.log.info(' * work done: operations returned %s - operations sent %s' % (len(results), no_messages_sent))

        return results
