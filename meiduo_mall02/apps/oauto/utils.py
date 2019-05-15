from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from apps.oauto.contents import OPENID_TOKEN_EXPIRES_TIME
from meiduo_mall02 import settings

import logging
logger = logging.getLogger('django')

# 13-itsdangerous的使用
def generic_openid_token(openid):
    #1.创建实例对象
    # s = Serializer(secret_key=settings.SECRET_KEY,expires_in=300)
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=OPENID_TOKEN_EXPIRES_TIME)
    #2.组织数据
    data = {
        'openid':openid
    }
    #3.加密数据
    token = s.dumps(data)
    #4.返回数据
    return token.decode()

#解密
#定义解密函数
def check_openid_tocken(tocken):

    #创建实例对象
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=OPENID_TOKEN_EXPIRES_TIME)
    try:
        #解密
        result = s.loads(tocken)
    except Exception as e:
        logger.error(e)
        return None
        #获取解密后的数据
    return result.get('openid')

