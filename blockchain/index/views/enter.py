import os
from django.http import JsonResponse
from Crypto.Hash import MD5
from django.contrib.auth.models import User
from django.contrib import auth
from index.models import *
import time


def create_token():
    data=str(time.time())
    digest = MD5.new(data.encode('utf-8')).hexdigest()
    return digest


def register(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user=User.objects.create_user(username=username, password=password)
            UserInfo.objects.create(user_id=user.id)
            tem='./users/temporary/'+username
            ack='./users/ack/'+username
            if not os.path.exists(tem):
                os.mkdir(tem)
            if not os.path.exists(ack):
                os.mkdir(ack)
            return JsonResponse({'success': 1})
        except Exception as e:
            print(e)
            return JsonResponse({'success': 0,'msg':'用户名已存在'})



def login(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            userinfo=UserInfo.objects.get(user_id=user.id)
            if userinfo.token==None:
                userinfo.token=create_token()
                userinfo.save()
            token=userinfo.token
            return JsonResponse({'success': 1,'token':token,'user':user.username})
        else:
            return JsonResponse({'msg': '账号密码错误'})
