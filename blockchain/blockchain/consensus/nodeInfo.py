import os

from rsa import *

MAIN_PUB=None
NODE_PUB={}

def getNodeKeys():
    global RSAPUB,RSAPIV,NODE_PUB,MAIN_PUB
    try:
        '''
        if RSAPUB !='':
            pub=open("./Keys/MyKey/RSA_PUB","rb")
            RSAPUB = RSA.import_key(pub.read())
            pub.close()

        piv=open("./Keys/MyKey/RSA_PIV","rb")
        RSAPIV=RSA.import_key(piv.read())
        piv.close()
        '''
        primary=open("./Keys/MainNode/MAIN_PUB", "rb")
        MAIN_PUB=RSA.import_key(primary.read())
        primary.close()

        files=os.listdir("./Keys")
        for file in files:
            url = "./Keys/" + file
            if os.path.isfile(url):
                f=open(url,"rb")
                NodeID=file[1:]
                NODE_PUB[NodeID]=RSA.import_key(f.read())
                f.close()
    except:
        raise Exception("Keys文件打开出错")




