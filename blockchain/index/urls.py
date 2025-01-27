from django.conf.urls import url
from django.urls import path
from .views import enter,backstage,user
app_name='index'
urlpatterns=[
    path('login',enter.login),
    path('register', enter.register),
    path('addnode', backstage.addnode),
    path('audit', backstage.audit),
    path('show',backstage.show),
    path('my',user.my),
    path('myupload',user.upload),
    path('upload',user.upload),
    path('searchAsset',backstage.showAsset),
    path('searchBlock',backstage.showBlock),
    path('broadcast',backstage.broadcast)
]