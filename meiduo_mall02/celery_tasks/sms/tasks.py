"""
    # 1.需要单独创建一个任务包,任务包中的py文件必须以 tasks.py作为我们的文件名
    # 2.生成者/任务 其本质就是 函数
    # 3.这个函数必须要经过 celery的实例对象的task装饰器装饰
    # 4.这个任务需要让celery自动检测

    #1.定义一个函数
    #2.调用云通讯中的发送短信的函数发送短信，并异常捕获
    #2+判断发送短信是否成功,不成功则下单失败
    #2++.用logger日志器记录日志
    #3.用任务的task装饰器去装饰
    #4.@app.task(bind=True,default_retry_delay=5,name='send_sms')参数分别表示（任务本身，延迟时间，对任务重命名）
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