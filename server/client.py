import socket
import sys

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(data + "\n", "utf-8"))

    print("Sent:     {}".format(data))

    # Receive data from the server and shut down
    while True:
        received = str(sock.recv(1024), "utf-8")
        if not received: break
        print("Received: {}".format(received))

    sock.close()
