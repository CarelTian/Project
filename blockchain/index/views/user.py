import os
import shutil
from django.http import JsonResponse
from Crypto.Hash import MD5
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.contrib import auth
import hashlib
from index.models import *
import socket
from json import *
import time

def send(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.191.1', 8334))
    sock.send(msg.encode())
    sock.close()

def digest(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as file:
        buf = file.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()
def my(request):
    if request.method =='GET':
        token=request.META.get('HTTP_TOKEN')
        info= UserInfo.objects.get(token=token)
        raw=tempAsset.objects.filter(user_id=info.user_id,state="已通过")
        data=[]
        for i in raw:
            a=model_to_dict(i)
            data.append(a)
        return JsonResponse({'success':1,'data':data})

def upload(request):
    if request.method=='GET':
        token=request.META.get('HTTP_TOKEN')
        info= UserInfo.objects.get(token=token)
        raw = tempAsset.objects.filter(user_id=info.user_id)
        data = []
        for i in raw:
            a = model_to_dict(i)
            data.append(a)
        return JsonResponse({'success': 1, 'data': data})
    if request.method=='POST':
            op = 'ack|'
            address=request.POST.get('address')
            type= request.POST.get('type')
            asset = request.POST.get('asset')
            node='N0'
            token = request.META.get('HTTP_TOKEN')
            info = UserInfo.objects.get(token=token)
            userid=info.user_id
            name = User.objects.get(id=userid).username
            file = request.FILES.get('file')
            path='./users/temporary/'+name+'/' + file.name
            with open(path, 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            md5=digest(path)
            tempAsset.objects.create(address=address,type=type,asset=asset,node=node,
                                     filename=file.name,user_id=userid,MD5=md5)
            return JsonResponse({'success': 1, 'msg': 'yes'})
