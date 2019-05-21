# 上传文件需要先创建fdfs_client.client.Fdfs_client的对象，并指明配置文件，如

from fdfs_client.client import Fdfs_client
client = Fdfs_client('utils/fastdfs/client.conf')
# 通过创建的客户端对象执行上传文件的方法

client.upload_by_filename('/home/python/Desktop/images/cat.jpg')