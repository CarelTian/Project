import json
from tools import (
    hash256,
)

class Asset:
    def __init__(self,filename,MD5):
        self.filename=filename
        self.MD5=MD5
    def serialize(self):
        js={'filename':self.filename,'MD5':self.MD5}
        return json.dumps(js)

    @classmethod
    def parse(cls,s):
        js=json.loads(s)
        f=js['filename']
        m=js['MD5']
        return cls(f,m)




class Tx:
    def __init__(self,sender,receiver,assets,sign,time):
        self.sender=sender
        self.receiver=receiver
        self.assets=assets
        self.sign=sign
        self.time=time

    def ID(self):
        return self.hash().hex()

    def hash(self):
        return hash256(self.serialize().encode())[::-1]

    @classmethod
    def parse(cls, s):
        js=json.loads(s)
        s=js['sender']
        r=js['receiver']
        a=Asset.parse(js['assets'])
        i=js['sign']
        t=js['time']
        return cls(s,r,a,i,t)

    def serialize(self):
        js={'sender':self.sender,'receiver':self.receiver,'assets':self.assets.serialize(),'sign':self.sign,'time':self.time}
        return json.dumps(js)


