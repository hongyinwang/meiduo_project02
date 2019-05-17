
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

#a:02自定义用户注册模型类,AbstractUser继承Django默认用户模型类
class User(AbstractUser):
    #定义字段
    mobile = models.CharField(max_length=11,unique=True,verbose_name='mobile')
    #补充用户模型类字段email_active
    email_active = models.BooleanField(default=False,verbose_name='邮箱验证状态')

    #定义标签
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    #定义每个数据对象的显示信息
    def __str__(self):
        return self.username

