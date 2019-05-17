import re
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from django_redis import get_redis_connection

from apps.oauto.models import OAuthQQUser
from apps.oauto.utils import generic_openid_token, check_openid_tocken
from apps.users.models import User
from meiduo_mall02 import settings
from utils.response_code import RETCODE
import logging
logger = logging.getLogger('django')


#ＱＱ登陆功能的实现
class QQAuthURLView(View):

    def get(self,request):
        # 普通方式qq登录页面的网址
        #login_url = 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=400'

        #动态方式拼接
        #接受请求对象,从那个网址进入的，将来成功登入之后回调的地址就是那个
        next = request.GET.get('next')

        #准备qq登录页面的网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state = next
                        )
        #拼接qq登录的路由
        login_url = oauth.get_qq_url()
        # 返回相应对象
        return http.JsonResponse({'code':RETCODE.OK,
                                  'errmsg':'OK',
                                  'login_url':login_url
                                  })

# openid绑定用户的实现
class OautoQQuserView(View):

    def get(self,request):
        #1.# 提取code请求参数
        code = request.GET.get('code')
        #根据code换取token
        #https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=101518219&client_secret=418d84ebdc7241efb79536886ae95224&redirect_uri=http://www.meiduo.site:8000/oauth_callback&code=17F8CD7F06AEE94CD572C939544C22F1

        if code is None:
            return http.HttpResponseBadRequest("参数有错误")
        #创建工具对象
        qq_OAuto = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            redirect_uri=settings.QQ_REDIRECT_URI,
            client_secret=settings.QQ_CLIENT_SECRET
        )
        #2.使用code换取token
        token = qq_OAuto.get_access_token(code)
        #３根据token换取openid
        openid = qq_OAuto.get_open_id(token)
        #4.根据openid判断用户信息是否存在
        #get方式请求不存在会爆出DoesNotExist,所以这里需要做异常处理
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #这里我们需要对openid进行加密
            openid_token = generic_openid_token(openid)
            return render(request, 'oauth_callback.html', context={'openid': openid_token})
            # pass
        else:
            # 5.如果存在则进行登陆跳转
            user = qquser.user
            # 6.保持登陆状态
            login(request,user)
            # 7.设置cookie
            response = redirect(reverse('contents:Index'))
            response.set_cookie('username',user.username,max_age=14*24*3600)
            # 8.跳转
            return response

    #openid绑定用户的实现２
    def post(self,request):
        #1.接受收据
        datas = request.POST
        mobile = datas.get('mobile')
        password = datas.get('password')
        sms_code_client = datas.get('sms_code')
        access_token = datas.get('access_token')
        #2验证数据
        #2.1判断参数是否齐全
        mobile = str(mobile)
        if not all([mobile,password,sms_code_client]):
            return http.HttpResponseBadRequest("参数不齐")
        #2.2判断手机号是否符合规则
        if not re.match(r'^1[3-9]\d{9}$', mobile):

            return http.HttpResponseBadRequest('请输入正确的手机号码')
        #2.3判断密码是否符合规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return http.HttpResponseBadRequest("请输入8-20位的密码")
        #2.4判断短信验证码是否符合规则
        #2.4.1链接数据库
        redis_conn = get_redis_connection('code')
        #2.4.2通过手机号获取短信验证码
        sms_code_server = redis_conn.get('sms_%s'%mobile)
        #2.4.3判断短信验证码是否存在
        if not sms_code_server:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '短信验证码不存在'})
        #2.4.4判断客户输入的短信验证码＝＝服务端短信验证码
        if sms_code_client != sms_code_server.decode():
            return render(request,'oauth_callback.html',{'sms_code_errmsg':'无效的短信验证码'})
        #2.5判断判断openid是否有效
        openid = check_openid_tocken(access_token)
        #2.5.1判断openid是否存在
        if openid is None:
            return http.HttpResponseBadRequest("openid不存在")
        try:
            #2.6判断手机号是否存在
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #3保存数据,不存在则创建一个用户
            user = User.objects.create_user(
                mobile = mobile,
                password = password,
                openid = openid
            )
        else:
            #3.存在则再次判断密码
            if not user.check_password(password):
                return http.HttpResponseBadRequest('密码错误')

        #将用户绑定openid
        try:
            OAuthQQUser.objects.create(
                openid=openid,
                user = user
            )
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest("数据库错误")

        #状态保持
        login(request,user)
        #设置cookie
        response = redirect(reverse('contents:Index'))
        # next = request.GET.get('state')
        response.set_cookie('username',user.username,max_age=14*24*3600)
        #返回响应
        return response