'''
    #生产者
    1:导入cerely
    2:配置cerely,让celery 去加载可能用到的django配置文件
    3:创建cerely实例,参数确保唯一性即可
    4:自动注册celery任务(参数任务包是路径)
'''

#1:导入cerely
from celery import Celery

#c2:配置cerely,让celery 去加载可能用到的django配置文件
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall02.settings")

#3:创建cerely实例,参数确保唯一性即可
celery_app = Celery('celery_tasks')


#4:自动注册celery任务(参数任务包是路径)
celery_app.autodiscover_tasks(['celery_tasks.sms'])