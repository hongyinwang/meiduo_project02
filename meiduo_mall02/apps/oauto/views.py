from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.shortcuts import render
from django.views import View

from .utils import generic_openid_token
from apps.oauto.models import OAuthQQUser
from meiduo_mall02 import settings
from utils.response_code import RETCODE

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
            response.set_cookie('username',user.username,max_arg=14*24*3600)
            # 8.跳转
            return response



