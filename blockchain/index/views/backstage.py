import os,sys
import shutil
from django.http import JsonResponse
import hashlib
from django.forms.models import model_to_dict
from django.db.models import Max
from django.contrib.auth.models import User
from index.models import *
import socket
from json import *
from blockchain.core.Ta import *
from blockchain.core.zerg import *

def digest(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as file:
        buf = file.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()

def send(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.191.1', 8334))
    sock.send(msg.encode())
    sock.close()


def addnode(request):
    op='addnode|'
    if request.method=='POST':
        file=request.FILES.get('file')
        with open('./Keys/'+file.name, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
        nodename=request.POST.get('nodename')
        ip=request.POST.get('ip')
        try:
            if nodename!= None and ip!=None:
                js={'nodename':nodename,'ip':ip}
                js=dumps(js)
                msg=op+js
                send(msg)
            return JsonResponse({'success':1})
        except WindowsError:
            return JsonResponse({'success':0,'msg':'区块链网络异常'})

def audit(request):
    if request.method =='GET':
        raw=tempAsset.objects.filter(state='未审核')
        data=[]
        for i in raw:
            a=model_to_dict(i)
            name=User.objects.get(id=i.user_id).username
            a['name']=name
            data.append(a)
        return JsonResponse({'success':1,'data':data})

    if request.method == 'POST':
        #token=request.META.get('HTTP_TOKEN')
        #info= UserInfo.objects.get(token=token)
        username=request.POST.get('username')
        user_id=User.objects.get(username=username).id
        filename=request.POST.get('filename')
        asset=request.POST.get('asset')
        op=request.POST.get('op')
        temp=tempAsset.objects.get(user_id=user_id,filename=filename,asset=asset)
        old="./users/temporary/"+username+'/'+filename
        ack="./users/ack/"+username+'/'+filename
        try:
            if op=='delete':
                if os.path.exists(old):
                    os.remove(old)
                temp.state='未通过'
            elif op=='accept':
                if os.path.exists(old):
                    shutil.move(old, ack)
                temp.state="已通过"
            temp.save()
            op = 'ack|'
            js = {'sender':'N0','receiver':temp.address,'type':temp.type,'asset':temp.asset,'filename':temp.filename,
                  'md5':temp.MD5}
            js = dumps(js)
            msg=op+js
            send(msg)
        except Exception as e:
            print(e)
            return JsonResponse({'success': 0, 'msg': '服务器出错'})
        return JsonResponse({'success': 1, 'msg': 'yes'})

def show(request):
    if request.method=='GET':
        raw = tempAsset.objects.filter(state='已通过')
        data = []
        for i in raw:
            a = model_to_dict(i)
            name = User.objects.get(id=i.user_id).username
            a['name'] = name
            data.append(a)
        return JsonResponse({'success': 1, 'data': data})

def showAsset(request):
    if request.method=='GET':
        address=request.GET.get('address')
        if address==None:
            raw = tempAsset.objects.filter(state='已通过')
        else:
            raw=tempAsset.objects.filter(state='已通过',address=address)
        data = []
        for i in raw:
            a=model_to_dict(i)
            dic={}
            dic['ID']=a['MD5']
            dic['asset']=a['asset']
            dic['node']=a['node']
            dic['state']=a['state']
            data.append(dic)
        return JsonResponse({'success': 1, 'data': data})

def showBlock(request):
    if request.method=='GET':
        block = request.GET.get('height')
        if block != None:
           # try:
                B = Block.objects.get(height=block)
                Bdata=[{'height':B.height,'hash':B.hash,'prevhash':B.prev,
                       'time':B.time,'nodenum':B.ack}]
                T = Transaction.objects.filter(blockId=block)
                Tdata=[]
                for i in T:
                    a=model_to_dict(i)
                    Tdata.append(a)
                return JsonResponse({'success': 1,'BlockData':Bdata,'TransData':Tdata})
            #except Exception as e:
                print(e)
                return JsonResponse({'success': 0, 'message':'区块不存在'})
        else:
            height=Block.objects.all().aggregate(Max('height'))['height__max']
            return JsonResponse({'success': 1, 'height': height})

def broadcast(request):
    op='broadcast|'
    try:
        if request.method == 'POST':
            content=request.POST.get('content')
            tx=Tx.parse(bytes.fromhex(content).decode())
            sign=tx.sign
            point=s256Point.parse(bytes.fromhex(sign['point']))
            sig=signature.parse(bytes.fromhex(sign['sign']))
            asset=tx.assets
            md5=asset.MD5
            ret=point.verify(z,sig)
            raw = tempAsset.objects.filter(address=tx.sender, MD5=md5, state='已通过').first()
            if not ret:
                return JsonResponse({'success': 0, 'msg': '数字签名验证失败'})
            elif point.address()!=tx.sender:
                return JsonResponse({'success': 0, 'msg': '签名和地址不匹配'})
            elif raw is None:
                return JsonResponse({'success': 0, 'msg': '虚拟财产不存在'})
            raw.address=tx.receiver
            raw.save()
            # Pass to core
            js = {'payload': content}
            js = dumps(js)
            msg = op + js
            send(msg)
            return JsonResponse({'success': 1, 'msg': 'yes'})

    except WindowsError:
        return JsonResponse({'success': 0, 'msg': '区块链服务未启动'})
    except:
        return JsonResponse({'success': 0, 'msg': '请输入合法的transaction hex'})


