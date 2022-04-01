#!/usr/bin/env python

from datetime import datetime
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
from typing import Tuple, List
from signal import signal, SIGINT
import os
import sys

class Server(object):
    def __init__(self):
        # Socket server declaration
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.tcp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # Variable that stores registered routes
        self.routes: List[Tuple[str, str, str]] = []

        # Custom interruption handler
        signal(SIGINT, self.signalHandler)

    def listen(self, port: int, callback=None):
        # Start socket server on given port
        self.tcp.bind(('0.0.0.0', port))
        self.tcp.listen(1)

        # Execute custom anonymous function
        callback()

        while True:
            # On new connections, create a new thread and call the handle function
            connection, client = self.tcp.accept()
            thread = Thread(target=self.handle, args=(connection, client))
            thread.start()

    def handle(self, connection: socket, client: Tuple[str, int]):
        # Parse connection parameters
        method, path, httpVersion = connection.recv(1024).decode("utf-8").split('\r\n')[0].split(' ')
        address, port = client

        # Print connection log
        print("%s (%s:%s) [%s] %s %s" %(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), address, port, method, path, httpVersion))

        # Verify if the connection can be resolved with registered routes
        for route in self.routes:
            if route[0] == path:    
                # Return the content of registered route    
                file = open(os.path.join(os.path.dirname(__file__), route[2]), 'rb')
                connection.send(Server.encodedHttpResponse(200, route[1], file.read()))
                file.close()
                connection.close()
                return

        # Return not found exception
        connection.send(Server.encodedHttpResponse(404, 'text/plain', f'No resource was found at \'{path}\''.encode()))
        connection.close()

    # Register route
    def registerRoute(self, route: str, contentType: str, filePath: str):
        self.routes.append((route, contentType, filePath))
    
    # Build encoded http response
    def encodedHttpResponse(status: int, contentType: str, body: bytes):
        httpVersion = 'HTTP/1.1'
        statusMessage = 'OK' if status == 200 else 'Not Found'
        date = 'Sun, 18 Oct 2012 10:36:20 GMT'
        server = 'Python Server'
        contentLenght = len(body)
        connection = 'Closed'
        charset = 'iso-8859-1'
        httpPesponse = f'{httpVersion} {status} {statusMessage}\r\nDate: {date}\r\nServer: {server}\r\nContent-Length: {contentLenght}\r\nConnection: {connection}\r\nContent-Type: {contentType}; charset={charset}\r\n\r\n'
        return httpPesponse.encode() + body
    
    # Handle system SIGINT interruption
    def signalHandler(self, sig, frame):
        self.tcp.close()
        self.tcp.shutdown(sig)
        sys.exit(sig)
