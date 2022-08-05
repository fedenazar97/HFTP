# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $
import base64
from pathlib import Path
import socket
from constants import *
from base64 import b64encode
from os import listdir


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.socket = socket
        self.directory = directory

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """

        remainder = ''

        while True:
            try:
                data = self.socket.recv(1024)
            except ConnectionResetError:
                return

            if not data:
                # El cliente cerró la conexión
                return

            try:
                chunk = data.decode('ascii')
            except UnicodeDecodeError:
                self.send_response(BAD_REQUEST)
                return

            chunks = (remainder + chunk).split('\r\n')

            if len(chunks) > 0:
                remainder = chunks[-1]
                chunks = chunks[:-1]

            for command in chunks:

                if '\n' in command:
                    self.send_response(BAD_EOL)
                    # Los errores 100 cortan la conexión con el cliente
                    return

                if '  ' in command:
                    self.send_response(BAD_REQUEST)
                    # Los errores 101 cortan la conexión con el cliente
                    # Esto evita argumentos vacios
                    return

                words = command.split(' ')

                if self.is_a_command(words[0]):
                    if words[0] == "get_slice":
                        if len(words) == 4:
                            self.get_slice(words[1], words[2], words[3])
                        else:
                            self.send_response(INVALID_ARGUMENTS)

                    if words[0] == "get_metadata":
                        if len(words) == 2:
                            self.get_metadata(words[1])
                        else:
                            self.send_response(INVALID_ARGUMENTS)

                    if words[0] == "get_file_listing":
                        if len(words) == 1:
                            self.get_file_listing()
                        else:
                            self.send_response(INVALID_ARGUMENTS)

                    if words[0] == "quit":
                        if len(words) == 1:
                            self.send_response(CODE_OK)
                            return
                        else:
                            self.send_response(INVALID_ARGUMENTS)
                else:
                    self.send_response(INVALID_COMMAND)

    def send_response(self, code, body=''):
        header = str(code) + ' ' + error_messages[code] + '\r\n'

        response = bytes(header + body, 'ascii')
        self.socket.sendall(response)

    def is_a_command(self, word):
        list_of_commands = ["get_file_listing",
                            "get_metadata", "get_slice", "quit"]
        return word in list_of_commands

    def is_valid_file_name(self, file_name):
        for char in file_name:
            if char not in VALID_CHARS:
                return False
        return True

    def is_long_filename(self, file_name):
        return len(file_name) > (2**8)-1

    def get_metadata(self, file_name):

        if not self.is_valid_file_name(file_name):
            self.send_response(INVALID_ARGUMENTS)
            return

        if self.is_long_filename(file_name):
            self.send_response(FILE_NOT_FOUND)
            return

        path = Path(self.directory + '/' + file_name)

        if path.is_file():
            metadata = path.stat().st_size
            header = str(metadata) + '\r\n'
            self.send_response(CODE_OK, header)
        else:
            self.send_response(FILE_NOT_FOUND)

    def get_slice(self, file_name, offset, size):

        if not self.is_valid_file_name(file_name):
            self.send_response(INVALID_ARGUMENTS)
            return

        if self.is_long_filename(file_name):
            self.send_response(FILE_NOT_FOUND)
            return

        try:
            offset = int(offset)
            size = int(size)
        except ValueError:
            self.send_response(INVALID_ARGUMENTS)
            return

        path = Path(self.directory + '/' + file_name)

        if path.is_file():
            file_size = path.stat().st_size

            if offset < 0 or offset > file_size:
                self.send_response(BAD_OFFSET)
                return

            if 0 <= size and offset + size <= file_size:
                file = open(self.directory + '/' + file_name, 'rb')
                array = file.read(file_size)
                text = array[offset:offset + size]
                text1 = base64.b64encode(text).decode('ascii')
                self.send_response(CODE_OK, text1 + '\r\n')
            else:
                self.send_response(INVALID_ARGUMENTS)
        else:
            self.send_response(FILE_NOT_FOUND)

    def get_file_listing(self):
        cad = '\r\n'.join(listdir(self.directory) + ['']) + '\r\n'
        self.send_response(CODE_OK, cad)
