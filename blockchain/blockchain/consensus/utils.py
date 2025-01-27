import threading
import json
from rsa import *
#<REQUEST,o,t,c>
class Request:
    def __init__(self,m,t,a):
        self.message=m
        self.Timestamp=t
        self.addr=a
    def serialize(self):
        js={"message":self.message,"Timestamp":self.Timestamp,"addr":self.addr}
        return json.dumps(js)
    @classmethod
    def parse(cls,s):
        js=json.loads(s)
        m=js['message']
        t=js['Timestamp']
        a=js['addr']
        return cls(m,t,a)

#<<PRE-PREPARE,v,n,d>,m>
class PrePrepare:
    def __init__(self,request,digest,sequenceID,sign):
        self.request=request
        self.digest=digest
        self.sequenceID=sequenceID
        self.sign=sign
    def serialize(self):
        js={"request":self.request,"digest":self.digest,"sequenceID":self.sequenceID,"sign":self.sign}
        return json.dumps(js)
    @classmethod
    def parse(cls,s):
        js=json.loads(s)
        r=js['request']
        d=js['digest']
        s=js['sequenceID']
        a=js['sign']
        return cls(r,d,s,a)

#<PREPARE,v,n,d,i>
class Prepare:
    def __init__(self,digest,sequenceID,NodeId,sign):
        self.digest=digest
        self.sequenceID=sequenceID
        self.NodeId=NodeId
        self.sign=sign
    def serialize(self):
        js={"digest":self.digest,"sequenceID":self.sequenceID,"NodeId":self.NodeId,"sign":self.sign}
        return json.dumps(js)
    @classmethod
    def parse(cls,s):
        js=json.loads(s)
        d=js['digest']
        s=js['sequenceID']
        n=js['NodeId']
        a=js['sign']
        return cls(d,s,n,a)

#<COMMIT,v,n,D(m),i>
class Commit:
    def __init__(self,digest,sequenceID,NodeId,sign):
        self.digest=digest
        self.sequenceID=sequenceID
        self.NodeId=NodeId
        self.sign=sign
    def serialize(self):
        js={"digest":self.digest,"sequenceID":self.sequenceID,"NodeId":self.NodeId,"sign":self.sign}
        return json.dumps(js)
    @classmethod
    def parse(cls,s):
        js=json.loads(s)
        d=js['digest']
        s=js['sequenceID']
        n=js['NodeId']
        a=js['sign']
        return cls(d,s,n,a)

#<REPLY,v,t,c,i,r>
class Reply:
    def __init__(self,NodeId,message):
        self.NodeId=NodeId
        self.message=message
    def serialize(self):
        js={"NodeId":self.NodeId,"message":self.message}
        return json.dumps(js)
    @classmethod
    def parse(cls,s):
        js=json.loads(s)
        n=js['NodeId']
        m=js['message']
        return cls(n,m)
