from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as msg
from Crypto import Random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from zerg import *
from tools import *
from Ta import *

import os
import time
class menu():
    def __init__(self, master=None):
        self.root = master
        self.root.title("工具集V1.2.1")
        self.root.geometry('500x350+300+100')
        self.root.resizable(False,False)
        self.createpage()
        self.page = Frame(self.root, width=500, height=300, relief='ridge', borderwidth=1)
        self.A()
        mainloop()
    def createpage(self):
        self.page = Frame(self.root, width=500, height=50,relief='ridge',borderwidth=1)
        self.page.pack(fill='x', padx=3, pady=2)
        self.Abu1 = Button(self.page, text="生成RSA公私钥",command=self.A)
        self.Abu1.pack(side='left',padx=50)
        self.Abu2 = Button(self.page, text="生成区块地址",command=self.B)
        self.Abu2.pack(side='left',padx=20)
        self.Abu3 = Button(self.page, text="生成交易序列",command=self.C)
        self.Abu3.pack(side='left',padx=40)
    def A(self):
        self.page.destroy()
        self.page = Frame(self.root, width=500, height=300, relief='ridge', borderwidth=1)
        self.page.pack(fill='x', padx=2, pady=1)
        self.AL1=Label(self.page,text="RSA伪随机加密器").place(x=150,y=10)
        self.AL2 = Label(self.page)
        self.AL2.place(x=20,y=100)
        self.Abu1 = Button(self.page, text="选择存放目录",command=self.dir)
        self.Abu1.place(x=40, y=40)
        self.Abu1 = Button(self.page, text="生成公私钥",command=self.GKey)
        self.Abu1.place(x=300, y=40)
    def dir(self):
        dir = filedialog.askdirectory(initialdir='../')
        self.AL2['text']=dir
    def GKey(self):
        directory=self.AL2['text']
        random_generator = Random.new().read
        # 获取一个rsa算法对应的密钥对生成器实例
        rsa = RSA.generate(1024, random_generator)
        private_pem = rsa.exportKey()
        with open(directory+"/RSA_PIV", 'wb') as f:
            f.write(private_pem)
        public_pem = rsa.publickey().exportKey()
        with open(directory+"/RSA_PUB", 'wb') as f:
            f.write(public_pem)
        msg.showinfo("提示","生成成功！！！")

    def B(self):
        self.page.destroy()
        self.page = Frame(self.root, width=500, height=300, relief='ridge', borderwidth=1)
        self.page.pack(fill='x', padx=2, pady=1)
        L1=Label(self.page,text="生成区块链账号").place(x=150,y=10)
        L2 = Label(self.page,text="输入助记符").place(x=100,y=60)
        L3 = Label(self.page, text="地址").place(x=120, y=150)
        L3 = Label(self.page, text="私钥").place(x=120, y=200)
        self.first=StringVar()
        self.second=StringVar()
        self.third = StringVar()
        Entry(self.page, width=30, textvariable=self.first).place(x=180, y=60)
        Entry(self.page, width=30, textvariable=self.second).place(x=180, y=150)
        Entry(self.page, width=30, textvariable=self.third).place(x=180, y=200)
        btn=Button(self.page, text="生成地址",command=self.address)
        btn.place(x=180,y=100)

    def address(self):
        now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        memo=self.first.get()
        z=int.from_bytes(hash256(bytes(memo,encoding='utf8')),'big')
        e = z + int.from_bytes(bytes(now, encoding='utf8'), 'big')
        address=(e*G).address()
        self.second.set(address)
        self.third.set(str(e))
    def C(self):
        self.page.destroy()
        self.page = Frame(self.root, width=500, height=300, relief='ridge', borderwidth=1)
        self.page.pack(fill='x', padx=2, pady=1)
        self.c1=StringVar()
        self.c2=StringVar()
        self.c3 = StringVar()
        self.c4 = StringVar()
        L1 = Label(self.page, text="生成交易序列").place(x=150, y=10)
        L2 = Label(self.page, text="发送地址").place(x=20, y=50)
        L3 = Label(self.page, text="接收地址").place(x=250, y=50)
        L4 = Label(self.page, text="私钥").place(x=20, y=100)
        L5 = Label(self.page, text="财产ID").place(x=250, y=100)
        Entry(self.page, width=20, textvariable=self.c1).place(x=80, y=50)
        Entry(self.page, width=20, textvariable=self.c2).place(x=320, y=50)
        Entry(self.page, width=20, textvariable=self.c3).place(x=80, y=100)
        Entry(self.page, width=20, textvariable=self.c4).place(x=320, y=100)
        btn=Button(self.page, text="点击生成",command=self.Trans)
        btn.place(x=400,y=170)
        self.text=Text(self.page,width=40,height=6)
        self.text.place(x=80,y=150)

    def Transaction(self):
        md5=self.c4.get()
        sender=self.c1.get()
        receiver=self.c2.get()
        key=int(self.c3.get())
        oval=key*G
        point=s256Point(oval.x,oval.y)
        sign=PrivateKey(key).sign(z)
        sig={'point':point.serialize(),'sign':sign.serialize()}
        asset=Asset("default",md5)
        t=Tx(sender,receiver,asset,sig,int(time.time()))
        stream=t.serialize().encode().hex()
        self.text.insert('1.0',stream)
    def Trans(self):
        self.text.delete(1.0,END)
        md5=self.c4.get()
        sender=self.c1.get()
        receiver=self.c2.get()
        key=int(self.c3.get())
        oval=key*G
        point=s256Point(oval.x,oval.y)
        sign=PrivateKey(key).sign(z)
        sig={'point':point.sec().hex(),'sign':sign.der().hex()}
        asset=Asset("default",md5)
        t=Tx(sender,receiver,asset,sig,int(time.time()))
        stream=t.serialize().encode().hex()
        self.text.insert('1.0',stream)
    def comeback(self):
        self.page1.destroy()
        self.createpage()
root=Tk()
menu(root)













