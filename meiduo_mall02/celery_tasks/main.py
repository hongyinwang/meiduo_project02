#生产者
#c1:导入cerely
from celery import Celery

#c2:配置cerely,让celery 去加载可能用到的django配置文件
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall02.settings")

#c3:创建cerely实例,参数确保唯一性即可
celery_app = Celery('celery_tasks')

#c4:加载celery配置
celery_app.config_from_object('celery_tasks.config')

#c5:自动注册celery任务
#参数任务包是路径
celery_app.autodiscover_tasks(['celery_tasks.sms'])