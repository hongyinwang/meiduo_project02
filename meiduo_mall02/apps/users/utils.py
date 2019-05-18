import re

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from apps.users.models import User

import logging
logger = logging.getLogger('django')

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


#生成邮箱验证链接
def generate_verify_email_url(user):
    """
    # 1.创建实例对象
    # 2.准备用户信息(user.id,user.email)
    # 2+给用户信息进行加密
    # 3.拼接验证路由
    # 4.返回路由
    :return:
    """
    # 1.创建实例对象
    serialize = Serializer(settings.SECRET_KEY, expires_in=3600)
    # 2.2.准备用户信息(user.id,user.email)
    data = {'user_id': user.id, 'email': user.email}
    # 2+给用户信息进行加密
    token = serialize.dumps(data).decode()
    # 3.拼接验证路由
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' +token
    # 4.返回路由
    return verify_url


#验证链接提取用户信息
def check_verify_email_token(token):
    """
    # 1.创建实例对象
    # 2.解密数据(异常处理)
    #     成功则解密
    #     解密失败则返回空
    # 3.获取数据(异常处理)
    #     不存在则返回空
    #     存在则返回对象user
    # 4.验证数据(use_id,user_email)
    :param token:
    :return:
    """
    # 1.创建实例对象
    serialize = Serializer(settings.SECRET_KEY,expires_in=3600)
    # 2.解密数据(异常处理)
    #     成功则解密
    #     解密失败则返回空
    try:
        loads_token = serialize.loads(token)
    except Exception as e:
        logger.error(e)
    else:
        # 3.获取数据(异常处理,怎么存的,怎么获取)
        #     不存在则返回空
        #     存在则返回对象user
        user_id = loads_token.get('user_id')
        user_email = loads_token.get('email')
        # 4.验证数据(use_id,user_email)
        try:
            user = User.objects.get(id=user_id,email=user_email)
        except User.DoesNotExist:
            return None
        else:
            return user


