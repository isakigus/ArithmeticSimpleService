import unittest
import StringIO
import py7zlib

from common import decompress_7zip_file, decompress_7zip_stream, get_log


class Test7zip(unittest.TestCase):
    def test_decompress_7zip_file(self):
        with open('operations.txt', 'r') as txt_file:
            content_txt = txt_file.read()
        path = 'operations.7z'
        file_content = decompress_7zip_file(path)[0]
        self.assertEqual(content_txt, file_content)

    def test_decompress_string_format_error(self):
        resp = StringIO.StringIO('supercalifrastico')
        try:
            decompress_7zip_stream(resp)
        except py7zlib.FormatError:
            self.assertTrue(True)

    def test_decompress_7zip_stream(self):
        with open('operations.7z', 'rb') as file7z:
            stream = file7z.read()
        resp = StringIO.StringIO(stream)
        response = decompress_7zip_stream(resp)
        self.assertTrue(isinstance(response, list))


class TestLogger(unittest.TestCase):
    def test_get_log(self):
        log = get_log('test_log', verbose=False)

        self.assertEquals(log.name, 'test_log')
        self.assertEquals(log.level, 20)

    def test_get_log_verbose(self):
        log = get_log('test_log1', verbose=True)

        self.assertEquals(log.name, 'test_log1')
        self.assertEquals(log.level, 10)
