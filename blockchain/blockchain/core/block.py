from tools import hash256
import json
from Ta import *
class Block:
    def __init__(self,height,prev_block,TxList,time):
        self.height = height
        self.prev_block = prev_block
        self.TxList=TxList
        self.time=time
    @classmethod
    def parse(cls, s):
        js=json.loads(s)
        h=js['height']
        p=js['prev_block']
        t=js['TxList']
        t=t.split('|')
        lt=[]
        for i in t:
            if i!='':
                lt.append(Tx.parse(i))
        tt=js['time']
        return cls(h,p,lt,tt)

    def serialize(self):
        TxSerial=''
        for tx in self.TxList:
            TxSerial+=tx.serialize()+'|'
        js={"height":self.height,"prev_block":self.prev_block,"TxList":TxSerial,"time":self.time}
        return json.dumps(js)
    def hash(self):
        s = self.serialize().encode()
        h256 = hash256(s)
        return h256[::-1].hex()

    def HttpBlock(self,num=1)->dict:
        ret={}
        ret['height']=self.height
        ret['hash']=self.hash()
        ret['prev_block']=self.prev_block
        ret['time']=self.time
        ret['num']=num
        TxList={}
        for i,t in enumerate(self.TxList):
            tx={'sender':t.sender,'receiver':t.receiver,'hash':t.ID(),'MD5':t.assets.MD5,'time':self.time}
            TxList[i+1]=tx
        ret['Trans']=json.dumps(TxList)
        return ret





