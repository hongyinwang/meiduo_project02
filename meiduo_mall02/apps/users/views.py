import re
from django import http
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
# Create your views here.
from django_redis import get_redis_connection

from apps.users.models import User


#1.导入logging
import logging
#2.创建(获取)日志实例
from apps.users.utils import generate_verify_email_url, check_verify_email_token
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin

logger = logging.getLogger('django')

from django.db import DatabaseError
# Create your models here.

#定义用户注册页面



class RegisterView(View):
    """用户注册"""
    #get请求方式
    def get(self, request):
        """

        :param request:
        :return:
        """

        return render(request, 'register.html')

    # post请求方式
    def post(self,request):
        """

        :param request:
        :return:
        """
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

#登陆页面的实现
class LoginView(View):

    def get(self,request):
        """

        :param request:
        :return:
        """
        return render(request,'login.html')

    def post(self,request):
        """
        :param request:
        :return:
        1.接受用户输入数据
        2.校验数据
        2.1参数是否齐全
        2.2用户名是否符合规则
        2.3密码是否符合规则
        2.4用django自带的认证系统去认证用户输入的信息是否和数据库相对应
            返回user对象
        2.5判断user对象是否存在
            不存在则返回登陆页及相关信息
        2.6判断用户是否属于登陆状态
            不登陆则设置过期时间为０
            登陆则设置过期时间None(即当浏览器回话结束时过期)
        3.保持登陆状态
        3+获取next参数
            #判断next参数是否存在，存在则跳转
            #不存在跳转到首页成功
        4.再次判断是否选择记住登陆状态(设置cockie,目的是用浏览器记住用户信息)
            #未登陆则设置过期时间浏览器回话结束时
            #登陆则设置过期时间一周
        5.返回响应

        """
        #1.接受用户输入数据
        datas = request.POST
        username = datas.get('username')
        password = datas.get('password')
        remembered = datas.get('remembered')

        #2.校验数
        #2.1判断参数是否齐全
        if not all([username,password]):
            return http.HttpResponseBadRequest("参数不齐全")
        #2.2用户名是否符合规则(5-20个字符)
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        #2.3密码是否符合规则(8-20个数字)
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        #2.4用django自带的认证系统去认证用户输入的信息是否和数据库相对应
            #返回user对象
        from django.contrib.auth import authenticate
        user = authenticate(username=username,password=password)
        #2.5判断user对象是否存在
        if user is None:
            return render(request,'login.html',context={'login_error_password':'用户名或者密码错误'})
        #2.6判断用户是否属于登陆状态
            # 不登陆则设置过期时间为０
            # 登陆则设置过期时间None(即当浏览器回话结束时过期)
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        #3.保持登陆状态
        login(request, user)
        #3+获取next参数
            #判断next参数是否存在，存在则跳转
            #不存在跳转到首页成功
        next = request.GET.get('next')
        if next:
            return redirect(next)
        else:
            response = redirect(reverse('contents:Index'))

        #4.再次判断是否选择记住登陆状态(设置cockie,目的是用浏览器记住用户信息)
            #未登陆则设置过期时间浏览器回话结束时
            #登陆则设置过期时间一周
        if remembered != 'on':
            response.set_cookie('username',user.username,max_age=None)
        else:
            response.set_cookie('username', user.username, max_age=14*24*3600)

        #5.返回相应
        return response

from django.contrib.auth import logout
#登出界面
class LogoutView(View):

    def get(self,request):
        # 调用系统的logout方法
        logout(request)
        # 根据username清除cookie信息，因为我们的首页是根据username来判断是否登陆的
        # 返回相应，设置cookie
        response = redirect(reverse('contents:Index'))
        response.delete_cookie('username')
        #返回相应
        return response

#用户中心页面
class UserCenterInfo(LoginRequiredMixin,View):
    def get(self,request):
        """
        1.提供个人信息
        2.返回响应
        :param request:
        :return:
        """
        #1.提供个人信息
        context = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active': request.user.email,

        }
        #2.返回响应
        return render(request,'user_center_info.html',context=context)

'''
LoginRequiredMixin 会进行一个重定向
我们这里是进行的loadsajax 请求,我们应该返回一个json数据
'''
#EmailView
class EmailView(LoginRequiredJSONMixin,View):
    """
        # 1.接受body数据
        # 1.1把接受的bytes===>json数据
        # 1.2把json转化为dict
        # 1.3获取数据
        # 2.验证数据
        # 2.1邮箱地址是否存在,符合规则
        # 3.更新数据(email数据)
        # 4+验证邮箱的后端实现(加密)
        # 4.发送激活邮件/异步发送邮件
        # 4.1准备发送邮箱数据(主题，消息，发件人，收件人(列表)，内容)
        # 4.2发送数据
        # 5.返回响应
    """
    def put(self,request):
        # 1接受body数据
        body_datas = request.body
        # 1.1把接受的bytes===>json数据
        json_datas = body_datas.decode()
        # 1.2把json转化为dict
        dict_datas= json.loads(json_datas)
        # 1.3获取数据
        email = dict_datas.get('email')

        # 2.验证数据
        # 2.1邮箱地址是否存在,符合规则
        if not email:
            return http.HttpResponseBadRequest('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseBadRequest('参数email有误')

        # 3.更新数据(email数据)
            #成功则保存
            #不成功则更新失败
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            # raise self.retry(exc=e, max_retries=3)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'更新失败'})

        # 4.发送激活邮件
        # 4.1准备发送邮箱数据(主题，消息，发件人，收件人(列表)，内容)
        # subject = '美多商城激活邮件'
        # message = ''
        # from_email = '美多商城<qi_rui_hua@163.com>'
        # recipient_list = [email]
        # html_message = "<a href='#'>有思路,不纠结</a>"
        #
        # # 4.2发送数据
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=from_email,
        #     recipient_list=recipient_list,
        #     html_message=html_message
        # )

        # 4.2改为celery发送数据
        # 异步发送验证邮件
        # 4+验证邮箱的后端实现(加密)
        # verify_url = '邮件验证链接'
        verify_url = generate_verify_email_url(request.user)
        #4.异步发送邮件验证
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)
        # 5.返回响应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})


#验证邮箱后端逻辑实现
class VerifyEmailView(View):
    """验证邮箱"""
    def get(self,request):
        """
        #1.接受参数(tocken)
        #2.校验参数
        #2.1判断参数(tocken)是否存在/过期
        #3通过check_verify_email_token方法获取对象
        #3.1判断获取对象是否为空
        #4.激活用户并保存(异常处理)
        #5.返回响应
        :param request:用户点击邮箱激活的链接地址发送的请求
        :return:返回的激活邮箱的验证结果
                返回用户中心页面
        """
        # 1.接受参数(tocken)
        token = request.GET.get('token')
        # 2.校验参数
        # 2.1判断参数(tocken)是否存在/过期
        if token is None:
            return http.HttpResponseBadRequest("缺少参数")
        # 3通过check_verify_email_token方法获取对象
        user = check_verify_email_token(token)
        # 3.1判断获取对象是否为空
        if not user:
            return http.HttpResponseBadRequest('用户不存在')
        # 4.激活用户并保存(异常处理)
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest('激活失败')
        # 5.返回响应
        return redirect(reverse('users:info'))


#收货地址界面
class