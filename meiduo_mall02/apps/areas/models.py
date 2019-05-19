from django.db import models

# Create your models here.
"""
    # 1.创建字段()
    # 2.创建标题Meta
    # 3.显示数据
"""
class Area(models.Model):
    '''省市区'''
    name = models.CharField(max_length=20,verbose_name='名称')
    parent = models.ForeignKey('self',on_delete=models.SET_NULL,related_name='subs',null=True,verbose_name="上级行政区划")

    class Meta:
        db_table = 'tb_areas'
        verbose_name= '省市区'
        verbose_name_plural='省市区'

    def __str__(self):
        return self.name



"""
    # 查询省的信息
    select * from tb_areas where parent_id is NULL;

    # ORM
    Area.objects.filter(parent=None)


    # 查询市的信息
    #查询区县信息
    select * from tb_areas where parent_id=130000;
    select * from tb_areas where parent_id=130600;

    # ORM
    Area.objects.filter(parent_id=130000)
    Area.objects.filter(parent_id=130600)

"""
