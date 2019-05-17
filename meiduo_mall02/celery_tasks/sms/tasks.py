"""
    执行者
    1.创建tasks.py的包
    2.创建函数
    3.这个函数必须用celery实例对象去装饰
"""

from apps.varifications.contents import YUNTONGXUN_EXPIRE_TIME
from libs.yuntongxun.sms import CCP
from celery_tasks.main import celery_app
import logging
logger = logging.getLogger('django')


@celery_app.task(bind=True,default_retry_delay=5,name='send_sms')
def send_sms_code(self,mobile,sms_code):
    try:
        result = CCP().send_template_sms(mobile, [sms_code, YUNTONGXUN_EXPIRE_TIME], 1)
        if result != 0:
            raise Exception('下单失败')
    except Exception as exc:
        logger.error(exc)
        # max_retries 设置最大的重试次数
        raise self.retry(exc=exc,max_retries=3)



# @celery_app.task
# def send_sms_code(mobile,sms_code):
#     CCP().send_template_sms(mobile, [sms_code, YUNTONGXUN_EXPIRE_TIME], 1)