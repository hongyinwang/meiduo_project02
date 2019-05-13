import re
from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


class UsernameMobileModelBackend(ModelBackend):
    #重写
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            #区分手机号和用户名
            #用户名
            if re.match(r'^1[3-9]\d{9}$',username):
                #匹配用户输入的username数据库中mobile是否一致
                user = User.objects.get(mobile=username)
            #密码
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        # 根据用户的信息来验证密码
        if user.check_password(password):
                return user

