#1.您的自定义存储系统必须是以下的子类 django.core.files.storage.Storage：
#2.Django必须能够在没有任何参数的情况下实例化您的存储系统。
# 这意味着任何设置都应该来自django.conf.settings
#3.您的存储类必须实现_open()和_save() 方法
# 以及适用于您的存储类的任何其他方法
#4.您的存储类必须是可解构的， 以便在迁移中的字段上使用时可以对其进行序列化。
# 只要您的字段具有可自行序列化的参数，就
# 可以使用 django.utils.deconstruct.deconstructible类装饰器（
# 这就是Django在FileSystemStorage上使用的）。

from django.utils.deconstruct import deconstructible
from meiduo_mall02 import settings
#1.您的自定义存储系统必须是以下的子类 django.core.files.storage.Storage：
from django.core.files.storage import Storage

# 只要您的字段具有可自行序列化的参数，就
# 可以使用 django.utils.deconstruct.deconstructible类装饰器（
# 这就是Django在FileSystemStorage上使用的）。

#重新url方法
@deconstructible
class MyStorage(Storage):
    # 2.Django必须能够在没有任何参数的情况下实例化您的存储系统。
    def __init__(self, fdfs_url=None):
        if not fdfs_url:
            fdfs_url = settings.FDFS_URL
        self.fdfs_url = fdfs_url
    # 3.您的存储类必须实现_open()和_save() 方法
    def _open(self, name, mode='rb'):
        pass
    def _save(self, name, content, max_length=None):
        pass

    # 4.您的存储类必须是可解构的， 以便在迁移中的字段上使用时可以对其进行序列化。
    def url(self,name):
        return self.fdfs_url + name