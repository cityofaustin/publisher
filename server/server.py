import socketserver

# Create a Request Handler
# In this TCP server case - the request handler is derived from StreamRequestHandler
class MyTCPHandler(socketserver.StreamRequestHandler):

    # handle() method will be called once per connection
    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()
        print(f"{self.client_address[0]} wrote:")
        print(self.data)
        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        self.wfile.write(self.data.upper())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print("It is on.")
        server.serve_forever()

# import socketserver
#
# class EchoRequestHandler(socketserver.BaseRequestHandler):
#
#     def handle(self):
#         # Echo the back to the client
#         data = self.request.recv(1024)
#         self.request.send(data)
#         return
#
# if __name__ == '__main__':
#     import socket
#     import threading
#
#     address = ('localhost', 0) # let the kernel give us a port
#     server = socketserver.TCPServer(address, EchoRequestHandler)
#     ip, port = server.server_address # find out what port we were given
#
#     t = threading.Thread(target=server.serve_forever)
#     t.setDaemon(True) # don't hang on exit
#     t.start()
#
#     # Connect to the server
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((ip, port))
#
#     # Send the data
#     message = 'Hello, world'
#     print('Sending : "%s"' % message)
#     len_sent = s.send(message)
#
#     # Receive a response
#     response = s.recv(len_sent)
#     print('Received: "%s"' % response)
#
#     # Clean up
#     s.close()
#     server.socket.close()
