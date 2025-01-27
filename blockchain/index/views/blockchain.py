import os,sys
from django.http import JsonResponse
from index.models import *
from json import *

def CreateBlock(request):
    if request.method=='POST':
        height=request.POST.get('height')
        hash = request.POST.get('hash')
        prev_block = request.POST.get('prev_block')
        time = request.POST.get('time')
        num= request.POST.get('num')
        TransList=loads(request.POST.get('Trans'))
        Block.objects.create(height=height, hash=hash, prev=prev_block, time=time,
                                 Transnum=len(TransList), ack=num)
        for i in TransList:
            t=TransList[i]
            Transaction.objects.create(blockId=height ,sender=t['sender'],receiver=t['receiver'],hash=t['hash'],
                              MD5=t['MD5'],time=t['time'])
        return JsonResponse({'success':1})
    return  JsonResponse({'success':0})

