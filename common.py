import StringIO
import logging
import time
import unittest

import py7zlib

wait = time.sleep
END_SEQUENCE = ('En_un_lugar_de_la_Mancha,_de_cuyo_nombre_no_quiero_acordarme'
                '_no_ha_mucho_tiempo_que_vivia_un_hidalgo'
                '_de_los_de_lanza_en_astillero_adarga_antigua'
                '_rocin_flaco_y_galgo_corredor')


class Test7zip(unittest.TestCase):
    def test_descompress_7zip_file(self):
        with open('operations.txt', 'r') as txt_file:
            content_txt = txt_file.read()
        path = 'operations.7z'
        file_content = descompress_7zip_file(path)[0]
        self.assertEqual(content_txt, file_content)

    def test_descompress_string_format_error(self):
        resp = StringIO.StringIO('supercalifrastico')
        try:
            descompress_7zip_stream(resp)
        except py7zlib.FormatError:
            self.assertTrue(True)

    def test_descompress_7zip_stream(self):
        with open('operations.7z', 'rb') as file7z:
            stream = file7z.read()
        resp = StringIO.StringIO(stream)
        response = descompress_7zip_stream(resp)
        self.assertTrue(isinstance(response, str))


def get_log(name, verbose):
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)
    logger = logging.getLogger(name)
    logger.info(' ... logging started ...')

    return logger


def descompress_7zip_stream(stream):
    archive, output = py7zlib.Archive7z(stream), []
    for item in archive.getnames():
        data = archive.getmember(item).read()
        output.append(data)

    return output


def descompress_7zip_file(file7zname):
    with open(file7zname, 'rb') as file7zip:
        return descompress_7zip_stream(file7zip)
