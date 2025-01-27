from tkinter import *
from socket import *
from random import choice
from threading import Thread

class ReceiveThread(Thread):
    def __init__(self, tcpCliSock):
        Thread.__init__(self)
        self.daemon = True  # 守护线程
        self.tcpCliSock = tcpCliSock
        self.buff=1024

    def run(self):
        while True:
            data = self.tcpCliSock.recv(self.buff)
            if not data:
                pass
