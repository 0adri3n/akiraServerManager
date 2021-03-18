import socket
import threading
import os


class Server(threading.Thread):

    def __init__(self, p):
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__p = p
        self.accept_connections()


    def accept_connections(self):

        ip = "127.0.0.1"
        port = self.__p

        self.s.bind((ip, port))
        self.s.listen(100)

        print("File transfer server started.")

        while True:

            c, addr = self.s.accept()

            handle = threading.Thread(target=self.handle, args=(c, addr))
            handle.start()

    def handle(self, c, addr):

        data = c.recv(1024).decode()

        if not os.path.exists(data):
            c.send("file-doesn't-exist".encode())

        else:
            c.send("file-exists".encode())
            print('Sending', data)
            if data != '':
                file = open(data, 'rb')
                data = file.read(1024)
                while data:
                    c.send(data)
                    data = file.read(1024)

                c.shutdown(socket.SHUT_RDWR)
                c.close()

