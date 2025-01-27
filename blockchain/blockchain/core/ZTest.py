from unittest import TestCase
from Ta import *
from block import *

class TransTest(TestCase):
    def test_serialization(self):
        a=Asset('1.txt','MD5')
        t=Tx('aaa','bbb',a,'sign','time')
        print(t.serialize())
        T=Tx.parse(t.serialize())
        self.assertEqual(T.serialize(),t.serialize())
     #   self.assertEqual(T,t)
    def test_block(self):
        a = Asset('1.txt', 'MD5')
        t1=Tx('sender','receiver',a,'sign','2023')
        b=Block(1,'0x00001',[t1],1)
        B=Block.parse(b.serialize()).serialize()
        self.assertEqual(B,b.serialize())