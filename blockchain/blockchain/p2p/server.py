import threading
import socket
import time
import sys,os
from consensus.pbft import *
import select
from handle import *

class Server:
    def __init__(self,TcpSock,pbft,NodeList):
        self.sock=TcpSock
        self.pbft=pbft
        self.NodeList=NodeList
        #self.handle={'broadcast':self.broadcast}
    def listen(self):
        inputs=[self.sock]
        while True:
            r_list,w_list,e_list=select.select(inputs,[],[])
            for event in r_list:
                if event is self.sock:
                    s,addr=event.accept()
                    inputs.append(s)
                    print('收到连接')
                else:
                  #  try:
                        data=event.recv(1024)
                        if data:
                            data=data.decode()
                            op,para=data.split('|')
                            if op=='check':
                                command=local[op](event,para)
                            else:
                                command=local[op](self.NodeList,para)
                        else:
                            inputs.remove(event)
                #    except socket.error as e:
                #        print(e)
                #        inputs.remove(event)
               #     except Exception as e:
                #        inputs.remove(event)
               #         print(e)

    def check(self,sock):
        op='check|'
        while True:
            lt = os.listdir('chaindata')
            payload=''
            for i in lt:
               payload+=i+'$'
            msg=op+payload
            sock.send(msg.encode())
            time.sleep(10)
    def file(self,sock):
        dir="chaindata/"
        while True:
            data=sock.recv(1024)
            obj=loads(data.decode())
            name = obj['name']
            size = obj['size']
            now=0
            file=dir+name
            f = open(file, 'ab')
            sock.send('ok'.encode())
            while now!=size:
                data = sock.recv(1024)
                f.write(data)
                now += len(data)
            sock.send('ok1'.encode())
            f.close()








