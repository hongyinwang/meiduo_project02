#执行者
#创建tasks.py的包
#创建函数
#这个函数必须用celery实例对象去装饰
from apps.varifications.contents import YUNTONGXUN_EXPIRE_TIME
from libs.yuntongxun.sms import CCP
from celery_tasks.main import celery_app

@celery_app.task
def send_sms_code(mobile,sms_code):
    CCP().send_template_sms(mobile, [sms_code, YUNTONGXUN_EXPIRE_TIME], 1)
