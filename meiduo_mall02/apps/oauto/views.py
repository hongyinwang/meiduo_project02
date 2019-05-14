from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.views import View

from meiduo_mall02 import settings
from utils.response_code import RETCODE


class QQAuthURLView(View):

    def get(self,request):
        #接受请求对象,从那个
        next = request.GET.get('next')
        #准备qq登录页面的网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state = next
                        )
        #拼接qq登录的路由
        login_url = oauth.get_qq_url()
        #返回相应对象
        return http.JsonResponse({'code':RETCODE.OK,
                                  'errmsg':'OK',
                                  'login_url':login_url
                                  })