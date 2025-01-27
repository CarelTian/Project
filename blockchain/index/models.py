from django.db import models
from django.conf import settings
# Create your models here.

class UserInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token=models.CharField(max_length=50,null=True)

class tempAsset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    MD5 = models.CharField(max_length=50)
    address=models.CharField(max_length=50)
    type=models.CharField(max_length=50)
    asset=models.CharField(max_length=50)
    filename=models.CharField(max_length=50)
    node=models.CharField(max_length=20)
    state=models.CharField(max_length=20,default="未审核")


class Node(models.Model):
    name=models.CharField(max_length=20)
    ip=models.CharField(max_length=20)
    PublicKey=models.CharField(max_length=20)

class Block(models.Model):
    height=models.CharField(max_length=10)
    hash=models.CharField(max_length=100)
    prev=models.CharField(max_length=100)
    time=models.CharField(max_length=20)
    Transnum=models.IntegerField()
    ack=models.IntegerField()

class Transaction(models.Model):
    blockId=models.IntegerField()
    sender=models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    hash = models.CharField(max_length=100)
    MD5 = models.CharField(max_length=50)
    time=models.IntegerField()
