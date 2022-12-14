#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $
from pathlib import Path
from ast import arg
import threading
import optparse
import socket
import connection
from constants import *


class Server(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print("Serving %s on %s:%s." % (directory, addr, port))
        # FALTA: Crear socket del servidor, configurarlo, asignarlo
        # a una dirección y puerto, etc.
        self.dir = directory
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if not Path(directory).is_dir():
            Path(directory).mkdir()
        
        self.s.bind((addr, port))
        self.s.listen()

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        
        while True:
            # FALTA: Aceptar una conexión al server, crear una
            # Connection para la conexión y atenderla hasta que termine.
            clientSocket,ad = self.s.accept()
            threading.Thread(target =self.serve2, args=(clientSocket,ad)).start()
            #se crea un hilo depues que el server haya resivido una peticion de un cliente 
            #el hilo se encarga del cliente y se vuelve al ciclo hasta que ingrese otro cliente 
            
            print("socket cliente e instancia de connection")
            
            
    def serve2(self,clientSocket,ad):
        newConnection = connection.Connection(clientSocket, self.dir)
        newConnection.handle()
        clientSocket.close()
        #funcion que gestiona los clientes que an sidos aceptados

def main():
    """Parsea los argumentos y lanza el server"""

    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar", default=DEFAULT_PORT)
    parser.add_option(
        "-a", "--address",
        help="Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option(
        "-d", "--datadir",
        help="Directorio compartido", default=DEFAULT_DIR)

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            "Numero de puerto invalido: %s\n" % repr(options.port))
        parser.print_help()
        sys.exit(1)

    server = Server(options.address, port, options.datadir)
    server.serve()
        


if __name__ == '__main__':
    main()
