import re
from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
# Create your views here.
from django_redis import get_redis_connection

from apps.users.models import User


#1.导入logging
import logging
#2.创建(获取)日志实例
logger = logging.getLogger('django')

from django.db import DatabaseError
# Create your models here.

#定义用户注册页面



class RegisterView(View):
    """用户注册"""
    #get请求方式
    def get(self, request):

        return render(request, 'register.html')

    # post请求方式
    def post(self,request):
        # ①接收数据 request.POST
        data = request.POST
        # ②分别获取数据 username,password
        #接受参数
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        allow = data.get('allow')
        sms_code_client = data.get('sms_code')

        # 校验参数
        # 判断参数是否齐全
        if not all([username,password,password2,mobile,allow,sms_code_client]):
            return http.HttpResponseBadRequest("参数不全")
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')

        #8.1验证用户提交的验证码是否和redis中保存的图形验证码是否一致
        #8.11链接redis
        redis_conn = get_redis_connection('code')
        # 2.2通过手机号获取uuid中短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 2.3redis中的短信验证码有可能过期，判断是否过期
        if not sms_code_server:
            return http.HttpResponseBadRequest("短信验证码已过期")
        # 2.4　比对
        if sms_code_server.decode().lower() != sms_code_client.lower():
            return http.HttpResponseBadRequest("短信验证码不一致")


        #保存注册数据
        try:
            user = User.objects.create_user(
                username = username,
                password = password,
                mobile = mobile
            )
        except Exception as e:
            logger.error(e)
            return render(request,'register.html',context={'register_errmsg': '注册失败'})
        #状态保持
        login(request, user)
        return redirect(reverse("contents:Index"))
        # return http.HttpResponse('ok')

#判断username是否重复
class UsernameCountView(View):

    def get(self, request, username):
        #校验
        #用户名查询登录
        count = User.objects.filter(username=username).count()

        #返回相应对象
        #将数据转换为json字符串,返回的是json数据
        return http.JsonResponse({'count': count})




