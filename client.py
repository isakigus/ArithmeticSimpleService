"""
This module contains the Client class for the Arithmetic service

client.py [-h] [--verbose] --port PORT --host HOST --output-file
                 OUT_FILE --input-file IN_FILE

python client.py --verbose --port 12345 --host 127.0.0.1
                --output-file out --input-file operations.7z
"""

import argparse
import socket

from common import get_log, wait, END_SEQUENCE


class Client:
    """Arithmetic service client, used to send the operations to the server"""

    def __init__(self, ip_address, port, log, output_file, input_file,
                 block_size):
        """
        Initializes the Client Object

        :param ip_address: server ip  address
        :param port: server port
        :param log: log object
        :param output_file: path where the results will be stored
        :param input_file: path where the input operations file is.
        :param block_size: number of characters to send via socket
        """
        self.log = log
        self.ip_address = ip_address
        self.port = port
        self.block_size = block_size
        self.input_filename = input_file
        self.output_filename = output_file
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def create_socket_connection(self):
        """
        Opens the connection with the server

        :return: None
        """
        n = 1
        while True:
            try:
                wait((n - 1) * 2)
                self.log.info('creating socket and connecting ... try #%s' % n)
                self.socket.connect((self.ip_address, self.port))
                self.log.info(
                    'socket connected to %s:%s' % (self.ip_address, self.port))
                break
            except Exception as ex:
                self.log.critical(ex)
                n += 1
                if n > 3:
                    break

    def send_request(self):
        """
        Transmission function

        :return: None
        """
        with open(self.input_filename, "rb") as input_fd:
            data = input_fd.read()

        if data:
            self.log.info('sending data ...')
            # self.socket.send(data + END_SEQUENCE)
            self.socket.send(data)
            self.socket.send(END_SEQUENCE)
            self.log.info('data sent')

    def get_response(self):
        """
        Receives the data from the server.

        :return: None
        """
        self.log.info('reading socket ...')
        no_chunks = 1
        response = self.socket.recv(self.block_size)
        self.log.debug(' ... chunk read ... %s' % no_chunks)

        while response[-len(END_SEQUENCE):] != END_SEQUENCE:
            no_chunks += 1
            response += self.socket.recv(self.block_size)
            self.log.debug(' ... chunk read ... %s' % no_chunks)

        response = response[:-len(END_SEQUENCE)]
        self.log.info(' *** end of reading ***')

        with open(self.output_filename, "wb") as output_fd:
            output_fd.write(response)

    def close_client(self):
        """
        Close client

        :return: None
        """
        self.socket.close()

    def run(self):
        """
        Runs the client, open the connection, and send the data, retrieves the
        results, finally close the client.

        :return: None
        """
        self.log.info('running ...')
        self.create_socket_connection()
        self.send_request()
        self.get_response()
        self.close_client()
        self.log.info('finished')


def main():
    """
    Main client entry point

    :return: None
    """
    parser = argparse.ArgumentParser(description='ArithmeticService-Client')

    parser.add_argument("--verbose",
                        help="increase output verbosity",
                        action="store_true")
    parser.add_argument("--port",
                        help="increase output verbosity",
                        type=int,
                        required=True)
    parser.add_argument("--host",
                        help="host ip of the arithmetic server",
                        required=True)
    parser.add_argument("--output-file",
                        dest="out_file",
                        help="path where results will be saved",
                        required=True)
    parser.add_argument("--input-file",
                        dest="in_file",
                        help="path of the input file, txt or 7z format",
                        required=True)
    parser.add_argument("--block_size",
                        dest="block_size",
                        help="socket data size transmission",
                        type=int,
                        default=4096)

    args = parser.parse_args()

    log = get_log('ArithmeticService-Client', args.verbose)
    client = Client(args.host, args.port, log, args.out_file, args.in_file,
                    args.block_size)
    client.run()


if __name__ == '__main__':
    main()
