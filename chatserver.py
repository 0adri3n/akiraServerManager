import socket
from threading import Thread



class listening_serv(Thread) :              
    def __init__(self, p):
        Thread.__init__(self) 
        # Connection Data
        self.host = '127.0.0.1'
        self.port = p

        # Starting Server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        # Lists For Clients and Their Nicknames
        self.clients = []
        self.nicknames = []
        self.receive()
        
        
    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle(self, client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024)
                self.broadcast(message)
            except:
                # Removing And Closing Clients
                index = self.clients.index(client)
                self.clients.remove(client)
                self.client.close()
                nickname = nicknames[index]
                broadcast('{} left!'.format(nickname).encode('ascii'))
                self.nicknames.remove(nickname)
                break
        
    def receive(self):
        while True:
            # Accept Connection
            client, address = self.server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            self.nicknames.append(nickname)
            self.clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            self.broadcast("{} joined!".format(nickname).encode('ascii'))
            client.send('Connected to server!'.encode('ascii'))

            # Start Handling Thread For Client
            thread = Thread(target=self.handle, args=(client,))
            thread.start()
                              






