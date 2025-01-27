import socket
import sys,os
import yaml,pickle
import time
from json import *
sys.path.append('../core')
from core.block import *
from core.Ta import *
from core.tools import *

PREFIX='http://localhost:8000/mpi/'
'''
def send(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 8334))
    sock.send(msg.encode())
    sock.close()
    print(sock)
while True:
        msg=input()
        send(msg)
'''
Tlist=[]

def addnode(NodeList,msg):
    try:
        js=loads(msg)
        name=js['nodename']
        ip=js['ip']
        port=8334
        f = open("./config.yaml", mode='r', encoding='utf-8')
        y = yaml.load(f, Loader=yaml.FullLoader)
        y['Node'][name]={'ip':ip,'port':port}
        f.close()
        f = open("./config.yaml", "w")
        yaml.dump(y, f, default_flow_style=False)
        f.close()
        NodeList.append({name:{'ip':ip,'port':port}})
        print('增加节点成功')
    except:
        print('增加节点失败')

def response(NodeList,msg):
    pass

def AckAsset(NodeList,msg):
    js = loads(msg)
    a = Asset(js['filename'], js['md5'])
    t = int(time.time())
    obj=Tx(js['sender'], js['receiver'], a, 'Bingo', t)
    Tlist.append(obj)
    if len(Tlist)==3:      #一个区块最多3个交易
        lt = os.listdir('chaindata')
        height = len(lt) + 1
        last_block = lt[-1]
        filename='chaindata/'+str(height-1).zfill(6)+'.pkl'
        with open('chaindata/'+last_block, "rb") as f:
            js = pickle.load(f)
            b=Block.parse(js)
            prev_block=b.hash()
        block= Block(height, prev_block, Tlist, t)
        with open(filename, "wb") as f:
            pickle.dump(block.serialize(), f)
        POST(PREFIX+'CreateBlock',block.HttpBlock())
        print('出块成功')
        Tlist.clear()

#留了个坑
def transfer(NodeList,msg):
    js= loads(msg)
    content=js['payload']
    tx=Tx.parse(bytes.fromhex(content).decode())
    Tlist.append(tx)
    print(len(Tlist))
    if len(Tlist) == 3:  # 一个区块最多3个交易
        t = int(time.time())
        lt = os.listdir('chaindata')
        height = len(lt) + 1
        last_block = lt[-1]
        filename = 'chaindata/' + str(height - 1).zfill(6) + '.pkl'
        with open('chaindata/' + last_block, "rb") as f:
            js = pickle.load(f)
            b = Block.parse(js)
            prev_block = b.hash()
        block = Block(height, prev_block, Tlist, t)
        with open(filename, "wb") as f:
            pickle.dump(block.serialize(), f)
        POST(PREFIX + 'CreateBlock', block.HttpBlock())
        print('出块成功')
        Tlist.clear()


def Sendfile(sock,msg):
    try:
        lt = os.listdir('chaindata')
        ask=msg.split('$')
        for file in lt:
            xfile='chaindata/'+file
            if file not in ask:
                size = os.stat(xfile).st_size
                sock.send(dumps({'name':file,'size':size}).encode())
                msg=sock.recv(1024)
                msg=msg.decode()
                if msg=='ok':
                    f = open(xfile, 'rb')
                    has_send = 0
                    while has_send != size:
                        File = f.read(1024)
                        sock.sendall(File)
                        has_send += len(File)
                    f.close()
                msg=sock.recv(1024)
                msg=msg.decode()
                if msg=='ok1':
                    print(file," 发送成功")
    except:
        print("sendfile error")



local={
    'addnode':addnode,
    'ping':response,
    'ack':AckAsset,
    'broadcast':transfer,
    'check':Sendfile
}
