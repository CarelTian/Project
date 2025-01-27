import threading
import json
from utils import *
from nodeInfo import *
from collections import defaultdict
import socket

REQUEST=1
PREPREPARE=2
PREPARE=3
COMMIT=4

NODE_NUM=3   #全局变量 测试用
class Node:
    def __init__(self,nodeID,RsaPub=None,RsaPIV=None):
        self.nodeID=nodeID
        self.RsaPub=RsaPub
        self.RsaPiv=RsaPIV

class Pbft:
    def __init__(self,node:Node,NodeList):
        self.node=node
        self.NodeList=NodeList
        self.lock=threading.Lock()
        self.sequenceID = 0
        self.prePareConfirmCount = defaultdict(int)
        self.commitConfirmCount = defaultdict(int)
        self.isCommitBordcast = defaultdict(bool)
        self.isReply = defaultdict(bool)
        getNodeKeys()

    #处理客户端请求
    def handleClientRequest(self,contentRaw):
        print("主节点接收到请求...")
        content=contentRaw.decode()
        try:
            r=Request.parse(content)
        except:
            print('Request解析出错')
            return
        self.sequenceIDAdd()
        digest=MD5.new(contentRaw).hexdigest()   #str类型
        self.messagePool[digest]=r
        Sign=RsaSign(digest,self.node.RsaPiv)
        pp=PrePrepare(contentRaw,digest,self.sequenceID,Sign)
        ppJson=pp.serialize()
        print("正在进行PrePrepare广播...")
        self.broadcast(PREPREPARE,ppJson)

    #处理欲准备消息
    def handlePrePrepare(self,contentRaw):
        print("收到主节点发送的PrePrepare")
        content=contentRaw.decode()
        try:
             pp=PrePrepare.parse(content)
        except:
            print("Prepare解析出错")
            return
        PrimaryKey=MAIN_PUB
        digest=pp.digest
        if digest !=MD5.new(pp.request).hexdigest():
            print("request摘要不相符，拒接广播")
        elif not RsaVerify(PrimaryKey,digest,pp.sign):
            print("主节点RSA验证失败，拒接广播")
        else:
            self.sequenceID=pp.sequenceID
            print("Preprepare阶段验证通过，准备进入Prepare...")
            self.messagePool[pp.digest]=pp.request
            sign=RsaSign(self.node.RsaPiv,digest)
            pre=Prepare(pp.digest,pp.sequenceID,self.node.nodeID,sign)
            pjson=pre.serialize()
            print("正在进行Prepare广播...")
            self.broadcast(PREPARE,pjson)

    def handlePrepare(self,contentRaw):
        content=contentRaw.decode()
        try:
            p=Prepare.parse(content)
        except:
            print("Prepare解析出错")
            return
        digest=p.digest
        pub=NODE_PUB[p.NodeId]
        if not RsaVerify(pub,digest,p.sign):
            print("节点RSA验证失败，拒接广播")
        else:
            self.lock.acquire()
            self.prePareConfirmCount[self.sequenceID]+=1
            Count=self.prePareConfirmCount[self.sequenceID]
            f=NODE_NUM//3
            #if Count>2*f and not self.isCommitBordcast[p.sequenceID]:
            if  not self.isCommitBordcast[p.sequenceID]:
                print("本节点收到至少2f个Prepare信息，正在进行Commit广播...")
                sign=RsaSign(self.node.RsaPiv,digest)
                c=Commit(digest,p.sequenceID,self.node.nodeID,sign)
                cjson=c.serialize()
                self.broadcast(COMMIT,cjson)
                self.isCommitBordcast[p.sequenceID]=True
            self.lock.release()

    def handleCommit(self,contentRaw):
        content = contentRaw.decode()
        try:
            c = Commit.parse(content)
        except:
            print("Prepare解析出错")
            return
        pub=NODE_PUB[c.NodeId]
        if not RsaVerify(pub,c.digest,c.sign):
            print("节点RSA验证失败，拒接广播")
        else:
            self.lock.acquire()
            self.commitConfirmCount[c.sequenceID]+=1
            count=self.commitConfirmCount[c.sequenceID]
            #if count >=NODE_NUM/3*2 and not self.isCommitBordcast[c.sequenceID]:
            if  not self.isCommitBordcast[c.sequenceID]:
                print("本节点收到2f+1个Commit信息，准备Reply")
                self.isCommitBordcast[c.sequenceID]=True
                #TCP转发client和收尾

    def handleRequest(self,data):
        data=data.decode()
        cmd,content=data.split('|')
        if cmd==REQUEST:
            self.handleClientRequest(content)
        elif cmd==PREPREPARE:
            self.handlePrePrepare(content)
        elif cmd==PREPARE:
            self.handlePrepare(content)
        elif cmd==COMMIT:
            self.handleCommit(content)
        else:
            #传区块
            pass


    def sequenceIDAdd(self):
        self.lock.acquire()
        self.sequenceID+=1
        self.lock.release()

    def broadcast(self,status,content):
        for node in self.NodeList:
            for last in node.values():
                address=(last['ip'],last['port'])
                send(address,status,content)

def send(address,status,content):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    msg=status+'|'+content
    msg=msg.encode()
    sock.send(msg)
    sock.close()
