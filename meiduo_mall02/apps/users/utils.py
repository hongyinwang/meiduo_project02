import re
from django.contrib.auth.backends import ModelBackend

from apps.users.models import User

#代码抽取
#定义一个函数
#哪里缺少补哪里，返回函数，验证没问题之后，删除源代码
def get_user_by_username(username):
    try:
        # 区分手机号和用户名
        # 用户名
        if re.match(r'^1[3-9]\d{9}$', username):
            # 匹配用户输入的username数据库中mobile是否一致
            user = User.objects.get(mobile=username)
        # 密码
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    return user

class UsernameMobileModelBackend(ModelBackend):
    #重写
    def authenticate(self, request, username=None, password=None, **kwargs):
        # try:
        #     #区分手机号和用户名
        #     #用户名
        #     if re.match(r'^1[3-9]\d{9}$',username):
        #         #匹配用户输入的username数据库中mobile是否一致
        #         user = User.objects.get(mobile=username)
        #     #密码
        #     else:
        #         user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     return None

        #调用封装好的区分手机号和密码功能函数
        user = get_user_by_username(username)
        # 根据用户的信息来验证密码
        #if user is not None是因为user可能为Ｎｏｎｅ
        if user is not None and user.check_password(password):
                return user

