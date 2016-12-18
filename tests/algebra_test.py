import unittest

from algebra import ArithmeticOperator


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
