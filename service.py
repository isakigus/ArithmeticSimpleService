import StringIO
import argparse
import multiprocessing
import socket

import py7zlib

from algebra import ArithmecticPool
from common import get_log, descompress_7zip_stream, END_SEQUENCE

"""
python service.py --verbose --port 12345 --host 127.0.0.1
"""


class Processor:
    def __init__(self, client_socket, block_size, log, messages_per_child):
        self.messages_per_child = messages_per_child
        self.socket = client_socket
        self.data = None
        self.log = log
        self.block_size = block_size

    def get_data_from_socket(self):
        self.log.info('reading socket ...')
        self.data = self.socket.recv(self.block_size)
        no_chunks = 1
        self.log.info(' ... chunck read ... %s' % no_chunks)

        while self.data[-len(END_SEQUENCE):] != END_SEQUENCE:
            no_chunks += 1
            self.data += self.socket.recv(self.block_size)
            self.log.info(' ... chunck read ... %s' % no_chunks)

        self.data = self.data[:-len(END_SEQUENCE)]
        self.log.info(' *** end of reading ***')
        self.descompress_data()

    def descompress_data(self):
        self.log.info(' * descompressing data ...')
        data_format = 'unknown'
        try:
            stream = StringIO.StringIO(self.data)
            self.data = descompress_7zip_stream(stream)[0]
            data_format = '7z'
        except py7zlib.FormatError:
            pass

        if isinstance(self.data, str):
            data_format = 'text'

        self.data = self.data.strip('\n')
        self.data = [i for i in self.data.split('\n') if i.strip()]
        self.log.info(' * data format found: %s' % data_format)

    def send_response(self):
        self.log.info(' * writting socket ...')

        no_childs = min([(len(self.data) / self.messages_per_child),
                         multiprocessing.cpu_count() * 3])
        no_childs = no_childs if no_childs else 1
        self.log.debug(' * number of calculated childs: %s' % no_childs)
        calulator = ArithmecticPool(no_childs, self.log)
        response = calulator.pool_processor(self.data)
        data_to_send = "\n".join(response)

        self.log.debug(' * sever responding ...')
        self.socket.send(data_to_send + END_SEQUENCE)

    def do_job(self):
        self.log.info(' * working ...')
        self.get_data_from_socket()
        self.send_response()
        self.socket.close()
        self.log.info(' * end processor ...\n\n')


class ArithmeticService:
    def __init__(self, log, ip_address, port, no_sockets, block_size, messages_per_child):
        self.messages_per_child = messages_per_child
        self.log = log
        self.ip_address = ip_address
        self.port = port
        self.block_size = block_size
        self.no_sockets = no_sockets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.info('  *** server running [ %s:%s ] ***' % (self.ip_address, self.port))

    def start_listenning(self):
        self.socket.bind((self.ip_address, self.port))
        self.socket.listen(self.no_sockets)

    def launch_process_message(self, client_socket):
        arithmetic_processor = Processor(client_socket, self.block_size, self.log, self.messages_per_child)
        arithmetic_worker = multiprocessing.Process(target=arithmetic_processor.do_job)
        arithmetic_worker.start()

    def run(self):
        self.start_listenning()
        while 1:
            (client_socket, address) = self.socket.accept()
            self.log.info('connetion accepetd %s' % str(address))
            self.launch_process_message(client_socket)

        self.log.info(' *** server stopped ***')


def parse_defult_args(args):
    try:
        import config
        host = args.host or config.default_ip_address
        port = args.port or config.default_port
        no_sockets = args.no_sockets or config.default_no_sockets
        block_size = args.block_size or config.default_socket_block_size
        messages_per_child = args.messages_per_child or config.default_messages_per_child
        return host, port, no_sockets, block_size, messages_per_child
    except ImportError:
        return args.host, args.port, args.no_sockets, args.block_size, args.messages_per_child


def main():
    parser = argparse.ArgumentParser(description='Blueliv-Arithmetic-Server')

    parser.add_argument("--verbose",
                        help="increase output verbosity",
                        action="store_true"
                        )
    parser.add_argument("--port",
                        help="connection port",
                        type=int
                        )
    parser.add_argument("--host",
                        help="host ip of the arithmetic server",
                        )
    parser.add_argument("--no_sockets",
                        type=int,
                        help="maximun number of server simultaneus conexions",
                        )
    parser.add_argument("--block_size",
                        type=int,
                        help="socket reading data size"
                        )
    parser.add_argument("--messages_per_child",
                        type=int,
                        help="number of messages to be processed for a arimethic pool worker"
                        )

    args = parser.parse_args()

    host, port, no_sockets, block_size, messages_per_child = parse_defult_args(args)

    log = get_log('Blueliv-Server', args.verbose)
    server = ArithmeticService(log, host, port, no_sockets, block_size, messages_per_child)

    try:
        server.run()
    except KeyboardInterrupt:
        log.info(' *** server stopped ***')


if __name__ == '__main__':
    main()
