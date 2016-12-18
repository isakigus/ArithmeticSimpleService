"""
This module contains the class ArithmeticOperator and ArithmeticPool
"""
import multiprocessing


class ArithmeticOperator:
    """
    This class is responsible of the arithmetic calculus and mathematics input
    validation
    """
    VALID = 'valid'
    OPERATORS = '+-*/'
    VALID_CHARSET = '1234567890 ' + OPERATORS

    @staticmethod
    def validate_operation_string(operation_string):
        """
        This function checks that all the characters in the input are valid,

        :param operation_string: input string with the operation
        :type operation_string: str
        :return: validation message, if is valid string the 'valid'
        :rtype: str
        """
        op = operation_string.strip()
        wrong_char_index = -1
        last_char_is_operator = False

        for idx, char in enumerate(operation_string):

            is_operator = char in ArithmeticOperator.OPERATORS

            if last_char_is_operator and is_operator:
                return 'two consecutive operators found, wrong syntax'

            if char not in ArithmeticOperator.VALID_CHARSET:
                wrong_char_index = idx
                break

            if char != ' ':
                last_char_is_operator = is_operator

        if wrong_char_index > 0:
            return 'wrong char, at position %s, not in %s' % (
                wrong_char_index, ArithmeticOperator.VALID_CHARSET)

        if not op[-1].isdigit():
            return 'last element is not valid'

        if not op[0].isdigit() and op[0] != '-':
            return 'first element is not valid'

        return ArithmeticOperator.VALID

    @staticmethod
    def operate(operation_string):
        """
        This function does the arithmetic operation

        :param operation_string: input string with the operation
        :type operation_string: str
        :return: result of the calculus
        :rtype: float
        """
        # first separation of associative terms is needed
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

                idx += 2

            # and we do the addition of all elements once
            # the associative terms have been calculated.
            reduction.append(total)

        return sum(reduction)

    @staticmethod
    def validate_and_operate(operation_string):
        """
        Validates the input and does the operation if pass the validation

        :param operation_string: input string with the operation
        :type operation_string: str
        :return: result or validation message
        """
        validation_msg = ArithmeticOperator.validate_operation_string(
            operation_string)

        if validation_msg == ArithmeticOperator.VALID:
            return ArithmeticOperator.operate(operation_string)
        else:
            return validation_msg


class ArithmeticPool:
    """
    This class is responsible to split the operations, and create jobs
    in order to resolve them
    """
    STOP_PILL = 'stop'
    TERMINATING_MSG = 'end'

    def __init__(self, number_children, log, validate_operations=True):
        """
        Initializes the ArithmeticPool

        :param number_children: number o workers to use
        :type number_children: int
        :param log: the logger object
        :type log: logger
        :param validate_operations: Tells if validation is done
        :type validate_operations: bool
        """
        self.number_children = number_children
        self.log = log
        self.validate_operations = validate_operations

    def job(self, i, conn):
        """
        Single work unit of the ArithmeticPool class

        :param i: process number
        :param conn: pipe where the results are delivered
        :return: None
        """
        while True:
            (msg, n) = conn.recv()
            # commented if not outupt is to verbose, uncomment when developing
            # or debugging
            # self.log.debug("process %s %s  - msgno %s" % (i, msg, n))

            if msg == ArithmeticPool.STOP_PILL:
                conn.send(ArithmeticPool.TERMINATING_MSG)
                self.log.debug("end sent %s" % i)
                break
            else:
                try:
                    if self.validate_operations:
                        result = ArithmeticOperator.validate_and_operate(msg)
                    else:
                        result = ArithmeticOperator.operate(msg)

                    return_msg = ("process[%s] response, input_line[%s]:"
                                  " %s = %s ") % (i, n, msg, result)
                    conn.send(return_msg)
                    self.log.debug(return_msg)

                except Exception as ex:
                    error_msg = ("error[%s] response, input_line[%s]:"
                                 " %s = %s ") % (i, n, msg, ex)
                    conn.send(error_msg)
                    self.log.debug(return_msg)

    def listener_loop(self, ps, q_out):
        """
        Main loop for ArithmeticPool

        :param ps: pool of process/workers
        :param q_out: output queue
        :return: None
        """
        while self.number_children:
            for p in ps:
                if p[1].poll():
                    msg_in = p[1].recv()
                    self.log.debug(msg_in)
                    if msg_in.strip() == ArithmeticPool.TERMINATING_MSG:
                        self.number_children -= 1
                        self.log.debug(
                            'process %s stopping , left running:%s' % (
                                p[0], self.number_children))
                    else:
                        q_out.put(msg_in)

    def pool_processor(self, operations_data):
        """
        Starts ArithmeticPool workers given an input data

        :param operations_data: input with the operations
        :return: results of the operations
        """
        process_list, output_queue = [], multiprocessing.Queue()
        duplicated_pipes_to_close = []

        for i in range(self.number_children):
            parent_conn, child_conn = multiprocessing.Pipe()

            # this is done because how forking works
            duplicated_pipes_to_close.append(child_conn)
            p = multiprocessing.Process(target=self.job, args=(i, child_conn,))
            p.daemon = True
            process_list.append((p, parent_conn))

        listener = multiprocessing.Process(target=self.listener_loop,
                                           args=(process_list, output_queue,))
        listener.daemon = True
        listener.start()

        for process_tuple in process_list:
            process_tuple[0].start()

        for pipe in duplicated_pipes_to_close:
            pipe.close()

        idx = no_messages_sent = 0

        for msg in operations_data:
            idx = idx if idx != self.number_children else 0
            process_list[idx][1].send((msg, no_messages_sent))
            no_messages_sent += 1
            idx += 1

        for process_tuple in process_list:
            process_tuple[1].send((ArithmeticPool.STOP_PILL, 0))
            self.log.debug('  -> stopping ... %s' % process_tuple[0])

        results = []

        while len(results) != no_messages_sent:
            element = output_queue.get()
            results.append(element)

        self.log.info((' * work done: operations returned %s - operations '
                       'sent %s') % (len(results), no_messages_sent))

        return results
