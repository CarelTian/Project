from Crypto import Random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
import os

#为节点创建RSA公私钥
def genRsaKeys():
    if not os.path.exists("./Keys"):
        os.mkdir("Keys")
    if not os.path.exists("./Keys/MyKey"):
        os.mkdir("./Keys/MyKey")
    if not os.path.exists("./Keys/MyKey/RSA_PIV"):
        # 获取一个伪随机数生成器
        random_generator = Random.new().read
        # 获取一个rsa算法对应的密钥对生成器实例
        rsa = RSA.generate(1024, random_generator)
        private_pem = rsa.exportKey()
        with open("./Keys/MyKey/RSA_PIV", 'wb') as f:
            f.write(private_pem)
        public_pem = rsa.publickey().exportKey()
        with open("./Keys/MyKey/RSA_PUB", 'wb') as f:
            f.write(public_pem)


def RsaSign(Pivkey,data):
    digest=MD5.new(data.encode('utf-8'))
    sig=pkcs1_15.new(Pivkey).sign(digest)
    return sig

def RsaVerify(Pubkey,data,sig)->bool:
    digest=MD5.new(data.encode('utf-8'))
    try:
        pkcs1_15.new(Pubkey).verify(digest, sig)
        return True
    except (ValueError,TypeError):
        pass
    return False

