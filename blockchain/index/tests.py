import socket

# Create your tests here.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.191.1', 8334))
sock.setblocking(False)