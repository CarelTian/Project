from unittest import TestCase
from rsa import *
from utils import *

class abcTest(TestCase):
    def test_digitalSignature1(self):
        piv=open("./Keys/MyKey/RSA_PIV",'rb')
        pub=open("./Keys/MyKey/RSA_PUB", 'rb')
        pkey = RSA.import_key(piv.read())
        puk = RSA.import_key(pub.read())
        sig=RsaSign(pkey,"Zerg")
        piv.close()
        pub.close()
        self.assertTrue(RsaVerify(puk,"Zerg",sig))

    def test_digitalSignature2(self):
        piv=open("./Keys/MyKey/RSA_PIV",'rb')
        pub=open("./Keys/MyKey/RSA_PUB", 'rb')
        pkey = RSA.import_key(piv.read())
        puk = RSA.import_key(pub.read())
        sig=RsaSign(pkey,"Zerg")
        piv.close()
        pub.close()
        self.assertFalse(RsaVerify(puk,"flood",sig))
    def test_RequestSerial(self):
        request=Request("hello",1121223,'127.0.0.1')
        ans='{"message": "hello", "Timestamp": 1121223, "addr": "127.0.0.1"}'
        self.assertEqual(ans,request.serialize())
        r2=Request.parse(ans)
        self.assertEqual(r2.serialize(),ans)
    def test_PrePrepareSerial(self):
        request = Request("hello", 1121223, '127.0.0.1')
        r=request.serialize()
        R=Request.parse(r)
        digest="abc"
        sequenceID=1
        sign="sign"
        prepare=PrePrepare(r,digest,sequenceID,sign)
        pre=prepare.serialize()
        self.assertEqual(pre,PrePrepare.parse(pre).serialize())


class Test_pbft(TestCase):
    def __init__(self):
        pass


