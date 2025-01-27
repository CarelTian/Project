
import hashlib
from io import BytesIO
import json
import hmac
import random
from tools import *
class Field:
    def __init__(self,num,prime):
        self.num=num
        self.prime=prime
    def __eq__(self, other):
        if other is None:
            return False
        return self.num==other.num and self.prime==other.prime
    def __add__(self, other):
        if self.prime!=other.prime:
            raise TypeError('两个数字不在一个有限域')
        num=(self.num+other.num)%self.prime
        return self.__class__(num,self.prime)
    def __sub__(self, other):
        if self.prime!=other.prime:
            raise TypeError('两个数字不在一个有限域')
        num=(self.num-other.num)%self.prime
        return self.__class__(num,self.prime)
    def __mul__(self, other):
        if self.prime!=other.prime:
            raise TypeError("两个数字不在一个有限域")
        num=(self.num*other.num)%self.prime
        return self.__class__(num,self.prime)
    def __truediv__(self, other):
        if self.prime!=other.prime:
            raise TypeError("两个数字不在一个有限域")
        num=(self.num*pow(other.num,other.prime-2,other.prime))%self.prime
        return self.__class__(num,self.prime)
    def __pow__(self, power):
        n=power%(self.prime-1)
        num=pow(self.num,n,self.prime)
        return self.__class__(num,self.prime)

class Point:
    def __init__(self,x,y,a,b):
        self.a=a
        self.b=b
        self.x=x
        self.y=y
        self.prime=a.prime
        if self.x is None and self.y is None:
            return
        if (self.y**2)!=(self.x**3+self.a*self.x+self.b):
           raise ValueError("不在曲线上")
    def __repr__(self):
        if self.x ==None and self.y==None:
            return "Point(infinity)"
        return "Point({},{})_{}_{} FieldElement({})".format(self.x.num,self.y.num,self.a.num,self.b.num,self.prime)
    def __eq__(self, other):
        return self.x==other.x and self.y==other.y \
            and self.a==other.a and self.b==other.b
    def __add__(self, other):
        if self.a!= other.a or self.b!=other.b:
            raise TypeError("不在一个曲线上")
        if self.x is None:
            return other
        if other.x is None:
            return self
        if self.x==other.x and self.y!=other.y:
            return self.__class__(None,None,self.a,self.b)
        if self.x!=other.x:
            s=(self.y-other.y)/(self.x-other.x)
            x=s**2-self.x-other.x
            y=s*(self.x-x)-self.y
            return self.__class__(x,y,self.a,self.b)
        if self==other:
            s = (Field(3,self.prime)*self.x**2+self.a)/(Field(2,self.prime)*self.y)
            x=s**2-Field(2,self.prime)*self.x
            y=s*(self.x-x)-self.y
            return self.__class__(x, y, self.a, self.b)
        if self==other and self.y==0*self.x:
            return self.__class__(None,None,self.a,self.b)
    def __rmul__(self, num):
        br=num
        current=self
        result=self.__class__(None,None,self.a,self.b)
        while br:
            if br&1:
                result+=current
            current+=current
            br>>=1
        return result

#secp256r1
P=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF  #2**224*(2**32-1)+2**192+2**96-1
A=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
B=0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
N=0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
X = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
Y = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5

class s256Field(Field):
    def __init__(self,num,prime=None):
        super().__init__(num=num,prime=P)
    def __repr__(self):
        return  '{:x}'.format(self.num).zfill(64)
    def sqrt(self):
        return self**((P+1)//4)

class s256Point(Point):
    def __init__(self,x,y,a=None,b=None):
        a,b=s256Field(A),s256Field(B)
        if type(x)==int:
            super().__init__(x=s256Field(x),y=s256Field(y),a=a,b=b)
           # self.xs = x
           # self.ys = y
        else:
            super().__init__(x=x,y=y,a=a,b=b)
            #if x!=None:
               # self.xs = x.num
                #self.ys = y.num

    def __rmul__(self, num):
        result=num%N
        return super().__rmul__(result)
    '''
    def serialize(self):
        js={'xs':self.xs,'ys':self.ys}
        return json.dumps(js)
    @classmethod
    def parseX(cls,s):
        js=json.loads(s)
        return cls(js['xs'],js['ys'])
    '''

    def verify(self,z,sig):
        s=pow(sig.s,N-2,N)
        u=z*s%N
        v=sig.r*s%N
        total=u*G+v*self
        return total.x.num==sig.r
    def sec(self):                #小端序序列化公钥
        if self.y.num%2==0:
            return b'\x02'+self.x.num.to_bytes(32,'little')
        else:
            return b'\x03'+self.x.num.to_bytes(32,'little')
    def hash160(self):
        return hash160(self.sec())
    def address(self):
        h160=self.hash160()
        prefix=b'\x3a'
        return encode_base58_checksum(prefix+h160)

    @classmethod
    def parse(self, sec_bin):        #解析公钥
        is_even = sec_bin[0] == 2
        x = s256Field(int.from_bytes(sec_bin[1:], 'little'))
        # right side of the equation y^2 = x^3 + 7
        alpha = x**3 +x*s256Field(A)+ s256Field(B)
        # solve for left side
        beta = alpha.sqrt()
        if beta.num % 2 == 0:
            even_beta = beta
            odd_beta = s256Field(P - beta.num)
        else:
            even_beta = s256Field(P - beta.num)
            odd_beta = beta
        if is_even:
            return s256Point(x, even_beta)
        else:
            return s256Point(x, odd_beta)

z = int.from_bytes(sha256(b'test'), 'big')
class signature:
    def __init__(self,r,s):
        self.r=r
        self.s=s

    def der(self):
        rbin = self.r.to_bytes(32, byteorder='big')
        rbin = rbin.lstrip(b'\x00')
        if rbin[0] & 0x80:
            rbin = b'\x00' + rbin
        result = bytes([2, len(rbin)]) + rbin  # <1>
        sbin = self.s.to_bytes(32, byteorder='big')
        sbin = sbin.lstrip(b'\x00')
        if sbin[0] & 0x80:
            sbin = b'\x00' + sbin
        result += bytes([2, len(sbin)]) + sbin
        return bytes([0x30, len(result)]) + result
    '''
    def serialize(self):
        js={'r':self.r,'s':self.s}
        return json.dumps(js)
    @classmethod
    def parseX(cls,s):
        js=json.loads(s)
        return cls(js['r'],js['s'])
    '''
    @classmethod
    def parse(cls, signature_bin):
        s = BytesIO(signature_bin)
        compound = s.read(1)[0]
        if compound != 0x30:
            raise SyntaxError("Bad Signature")
        length = s.read(1)[0]
        if length + 2 != len(signature_bin):
            raise SyntaxError("Bad Signature")
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Bad Signature")
        rlength = s.read(1)[0]
        r = int.from_bytes(s.read(rlength), 'big')
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Bad Signature")
        slength = s.read(1)[0]
        s = int.from_bytes(s.read(slength), 'big')
        if len(signature_bin) != 6 + rlength + slength:
            raise SyntaxError("Bad Signature")
        return cls(r, s)


class PrivateKey:
    def __init__(self,secert):
        self.secert=secert
        self.point=secert*G
    def hex(self):
        return '{:x}'.format(self.secert).zfill(64)
    def sign(self,z):
        #k=random.randint(0,N)     #伪随机数不安全
        k=self.deter_k(z)
        r=(k*G).x.num
        k_inf=pow(k,N-2,N)
        s=(z+r*self.secert)*k_inf%N
        if s>N/2:
            s=N-s
        return signature(r,s)
    def deter_k(self,z):
        k=b'\x00'*32
        v=b'\x01'*32
        if z>N:
            z-=N
        z_bytes=z.to_bytes(32,'big')
        secrets_byte=self.secert.to_bytes(32,'big')
        s256=hashlib.sha256
        k=hmac.new(k,v+b'\x00'+secrets_byte+z_bytes,s256).digest()
        v=hmac.new(k,v,s256).digest()
        k = hmac.new(k, v + b'\x01' + secrets_byte + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        while True:
            v=hmac.new(k,v,s256).digest()
            candidate=int.from_bytes(v,'big')
            if candidate>=1 and candidate<N:
                return candidate
            k=hmac.new(k,v+b'\x00',s256).digest()
            v=hmac.new(k,v,s256).digest()
    def wif(self):
        secret_bytes=self.secert.to_bytes(32,'little')
        prefix=b'\x66'
        suffix=b'\x01'
        return encode_base58_checksum(prefix+secret_bytes+suffix)



G=s256Point(X,Y)