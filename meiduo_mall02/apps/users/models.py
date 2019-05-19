
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

#a:02自定义用户注册模型类,AbstractUser继承Django默认用户模型类



class User(AbstractUser):
    #定义字段
    mobile = models.CharField(max_length=11,unique=True,verbose_name='mobile')
    #补充用户模型类字段email_active
    email_active = models.BooleanField(default=False,verbose_name='邮箱验证状态')
    #补充用户模型字段default_address
    # default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,on_delete=models.SET_NULL, verbose_name='默认地址')

    #定义标签
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    #定义每个数据对象的显示信息
    def __str__(self):
        return self.username

# from utils.models import BaseModel
# class Address(BaseModel):
#     '''用户地址'''
#     user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='addresses',verbose_name='省')
#     title = models.CharField(max_length=20,verbose_name='地址名称')
#     receiver= models.CharField(max_length=20,verbose_name='收货人')
#     province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses',verbose_name='省')
#     city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
#     district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses',verbose_name='区')
#     place = models.CharField(max_length=50, verbose_name='地址')
#     mobile = models.CharField(max_length=11, verbose_name='手机')
#     tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
#     email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
#     is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
#
#     class Meta:
#         db_table = 'tb_address'
#         verbose_name = '用户地址'
#         verbose_name_plural = verbose_name
#         ordering = ['-update_time']# 根据更新的时间倒叙