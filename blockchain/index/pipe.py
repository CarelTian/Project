from django.conf.urls import url
from django.urls import path
from .views import blockchain
app_name='index'
urlpatterns=[
    path('CreateBlock',blockchain.CreateBlock),
]