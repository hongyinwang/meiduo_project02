from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.response_code import RETCODE

# 1.重写LoginRequiredMixin
class LoginRequiredJSONMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        """
        1.重写LoginRequiredMixin(目的是用到了这个类的handle_no_permission方法，
            但是这个类中没有返回json对象的方法，所以要重写)
        2.返回相应对象
        :return:
        """

        # 2.返回相应对象
        return http.JsonResponse({'code':RETCODE.SESSIONERR,'errmsg':'未登录'})