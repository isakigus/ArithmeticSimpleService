"""
This module contains the `Processor` class and ArithmeticService `class`

usage:

    python service.py --verbose --port 12345 --host 127.0.0.1


-------------------------------
"""

import StringIO
import argparse
import multiprocessing
import socket

import py7zlib

from algebra import ArithmeticPool
from common import get_log, decompress_7zip_stream, END_SEQUENCE


class Processor:
    """
    This class is responsible for create teh poll of worker and communicate
    the input and the result with the service.
    """

    def __init__(self, client_socket, block_size, log, messages_per_child):
        """
        Initializes the Processor class, given a socket.
        
        :param client_socket: connection socket
        :param block_size: size of the socket data block
        :param log: log object
        :param messages_per_child: limit of messages
        """
        self.messages_per_child = messages_per_child
        self.socket = client_socket
        self.data = None
        self.log = log
        self.block_size = block_size

    def get_data_from_socket(self):
        """
        Read socket connection.

        :return: None
        """
        self.log.info('reading socket ...')
        self.data = self.socket.recv(self.block_size)
        no_chunks = 1
        self.log.debug(' ... chunk read ... %s' % no_chunks)

        while self.data[-len(END_SEQUENCE):] != END_SEQUENCE:
            no_chunks += 1
            self.data += self.socket.recv(self.block_size)
            self.log.debug(' ... chunk read ... %s' % no_chunks)

        self.data = self.data[:-len(END_SEQUENCE)]
        self.log.info(' *** end of reading ***')
        self.decompress_data()

    def decompress_data(self):
        """
        Gets the binary stream and inflates it

        :return: None
        """
        self.log.info(' * decompressing data ...')
        data_format = 'unknown'
        try:
            stream = StringIO.StringIO(self.data)
            self.data = decompress_7zip_stream(stream)[0]
            data_format = '7z'
        except py7zlib.FormatError:
            pass

        if isinstance(self.data, str):
            data_format = 'text'

        self.data = self.data.strip('\n')
        self.data = [i for i in self.data.split('\n') if i.strip()]
        self.log.info(' * data format found: %s' % data_format)

    def send_response(self):
        """
        Sends results to the service

        :return: None
        """
        self.log.info(' * writing socket ...')

        no_children = min([(len(self.data) / self.messages_per_child),
                           multiprocessing.cpu_count() * 3])
        no_children = no_children if no_children else 1
        self.log.debug(' * number of calculated children: %s' % no_children)
        calculator = ArithmeticPool(no_children, self.log)
        response = calculator.pool_processor(self.data)
        data_to_send = "\n".join(response)

        self.log.info(' * sever responding ...')
        self.socket.send(data_to_send + END_SEQUENCE)

    def do_job(self):
        """
        Main function of teh processor/worker object

        :return: None
        """
        self.log.info(' * working ...')
        self.get_data_from_socket()
        self.send_response()
        self.socket.close()
        self.log.info(' * end processor ...\n\n')


class ArithmeticService:
    """
    This class is responsible of:
    - Do the connections with all clients
    - Start a Processor object when data from client is received.
    """

    def __init__(self, verbose, ip_address, port, no_sockets, block_size,
                 messages_per_child):
        """
        :param verbose: log level
        :param ip_address: the ip where teh server is running
        :param port: port where the connection to the server is done
        :param no_sockets: number of simultaneous clients that server can handle
        :param block_size:
        :param messages_per_child:
        """
        self.verbose = verbose
        self.messages_per_child = messages_per_child
        self.log = get_log('ArithmeticService', self.verbose)
        self.ip_address = ip_address
        self.port = port
        self.block_size = block_size
        self.no_sockets = no_sockets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.info(
            '  *** server running [ %s:%s ] ***' % (self.ip_address, self.port))

    def start_listening(self):
        """
        Start server to listen incoming connections.

        :return: None
        """
        self.socket.bind((self.ip_address, self.port))
        self.socket.listen(self.no_sockets)

    def launch_process_message(self, client_socket, address):
        """
        Create a processor in order to do the calculation in
        a separated process.

        :param client_socket: connection between process and server
        :param address: server address
        :return: None
        """
        log = get_log('ArithmeticService-Server: conn [ %s:%s ]' % address,
                      self.verbose)
        arithmetic_processor = Processor(client_socket, self.block_size, log,
                                         self.messages_per_child)
        arithmetic_worker = multiprocessing.Process(
            target=arithmetic_processor.do_job)
        arithmetic_worker.start()

    def run(self):
        """
        Starts the server. Go!

        :return: None
        """
        self.start_listening()
        while 1:
            (client_socket, address) = self.socket.accept()
            self.log.info('connection accepted %s' % str(address))
            self.launch_process_message(client_socket, address)

        self.log.info(' *** server stopped ***')


def parse_default_args(args):
    """
    This functions parses the different parameters that can be pass thought cli.

    :param args: List of input arguments
    :return: host, port, no_sockets, block_size, messages_per_child
    """
    try:
        import config
        host = args.host or config.default_ip_address
        port = args.port or config.default_port
        no_sockets = args.no_sockets or config.default_no_sockets
        block_size = args.block_size or config.default_socket_block_size
        messages_per_child = args.messages_per_child or \
                             config.default_messages_per_child
        return host, port, no_sockets, block_size, messages_per_child
    except ImportError:
        return (args.host, args.port, args.no_sockets,
                args.block_size, args.messages_per_child)


def main():
    """
    Service main function.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description='ArithmeticService-Arithmetic-Server')

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
                        help="maximum number of server simultaneous connexions",
                        )
    parser.add_argument("--block_size",
                        type=int,
                        help="socket reading data size"
                        )
    parser.add_argument("--messages_per_child",
                        type=int,
                        help=("number of messages to be processed for"
                              " a arithmetic pool worker")
                        )

    args = parser.parse_args()

    host, port, no_sockets, block_size, messages_per_child = parse_default_args(
        args)

    server = ArithmeticService(args.verbose, host, port, no_sockets, block_size,
                               messages_per_child)

    try:
        server.run()
    except KeyboardInterrupt:
        msg = ' *** server stopped ***'
        if server and hasattr(server, 'log'):
            server.log.info(msg)
        print msg


if __name__ == '__main__':
    main()
