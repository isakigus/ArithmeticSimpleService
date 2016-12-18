"""
This module has some utils that can be used in any other
module of the application.
"""

import logging
import time
import py7zlib

wait = time.sleep
END_SEQUENCE = ('En_un_lugar_de_la_Mancha,_de_cuyo_nombre_no_quiero_acordarme'
                '_no_ha_mucho_tiempo_que_vivia_un_hidalgo'
                '_de_los_de_lanza_en_astillero_adarga_antigua'
                '_rocin_flaco_y_galgo_corredor')


def get_log(name, verbose):
    """
    This function return a logger to be used.

    :param name: log name
    :type name: str
    :param verbose: Level of output
    :type verbose: bool
    :return: logger
    :rtype: logger object
    """
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.info(' ... logging started ...')

    return logger


def decompress_7zip_stream(stream):
    """
    This file decompress a binary stream to a human readable list

    :param stream:
    :return: None
    """
    archive, output = py7zlib.Archive7z(stream), []
    for item in archive.getnames():
        data = archive.getmember(item).read()
        output.append(data)

    return output


def decompress_7zip_file(file_7z_name):
    """
    Decompress a binary file

    :param file_7z_name: name where the compressed files is
    :return: return a string with the data decompressed from compressed file
    """
    with open(file_7z_name, 'rb') as file7zip:
        return decompress_7zip_stream(file7zip)
