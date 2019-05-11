
from django.conf.urls import url,include
from django.contrib import admin

from apps.varifications import views

urlpatterns = [

    # 校验验证码
    url(r'^image_codes/(?P<uuid>[\w-]+)/', views.ImageCodeView.as_view(), name='imagecodes'),

    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/', views.SMSCodeView.as_view(), name='smscodeview'),

]