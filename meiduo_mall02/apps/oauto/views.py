from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.shortcuts import render
from django.views import View

from meiduo_mall02 import settings
from utils.response_code import RETCODE

#qq登录功能的实现
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

# 视图的展示
class OautoQQuserView(View):

    def get(self,request):
        return render(request,'oauth_callback.html')