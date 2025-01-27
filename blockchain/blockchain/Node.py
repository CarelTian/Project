import yaml,pickle
import sys,os,time
import time
sys.path.append('./core')
sys.path.append('./p2p')
sys.path.append('./consensus')
from p2p.server import *
from core.tools import *
from core.block import *
from core.Ta import *

#节点信息
f=open("./config.yaml",mode='r',encoding='utf-8')
y=yaml.load(f,Loader=yaml.FullLoader)
f.close()
ip,port=y['bind']['ip'],y['bind']['port']
NodeList=[y['Node']]
#读取公私钥
piv = open("./Keys/MyKey/RSA_PIV", 'rb')
pub = open("./Keys/MyKey/RSA_PUB", 'rb')
pkey = RSA.import_key(piv.read())
puk = RSA.import_key(pub.read())
piv.close()
pub.close()
#创世区块检测
mainpub,mypub='./Keys/MyKey/RSA_PUB','./Keys/MainNode/MAIN_PUB'
if  digest(mypub)==digest(mainpub):
    GenesisBlock='./chaindata/000000.pkl'
    if  not os.path.exists(GenesisBlock):
        filename='Satoshi Nakamoto has created Bitcoin in 2008.Today,a great innovative Blockchain named ZergFlood will change the world.'
        md5=66666
        height,prev_block=1,'0'*64
        a=Asset(filename,md5)
        t=int(time.time())
        TxList=[Tx('lyt','ZergFlood',a,'Bingo',t)]
        genesis=Block(height,prev_block,TxList,t)
        with open(GenesisBlock,"wb") as f:
            pickle.dump(genesis.serialize(),f)
        try:
            POST(PREFIX+'CreateBlock',genesis.HttpBlock())
        except:
            #面向无连接
            pass


#初始化服务器
node=Node(y['bind']['id'],puk,pkey)
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((ip, port))
sock.listen(10)
pbft=Pbft(Node,NodeList)
tcpserver=Server(sock,pbft,NodeList)
t1=threading.Thread(target=tcpserver.listen)
t1.start()
if NodeList[0]['MainNode']['ip']!=ip:
        ip=NodeList[0]['MainNode']['ip']
        port=int(NodeList[0]['MainNode']['port'])
        arg=(ip,port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(arg)
        t2=threading.Thread(target=tcpserver.check,args=(sock,))
        t2.start()
        t3=threading.Thread(target=tcpserver.file,args=(sock,))
        t3.start()
while True:
    time.sleep(1)
    pass