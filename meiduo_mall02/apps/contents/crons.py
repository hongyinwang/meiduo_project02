import os
import time

from django.template import loader

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from meiduo_mall02 import settings

#首页静态化
def generate_static_index_html():
    """
    定义:用户直接去静态服务器，访问处理好的静态html文件。
    需求:为什么要静态化
        减少数据库查询次数。
        提升页面响应效率。

    # 1.生成静态的主页html文件
    # 2.获取频道和分类
    # 3.获取广告内容
    # 4.渲染模板
    # 5.获取首页模板文件
    :return:
    """
    # 1.生成静态的主页html文件
    print('%s:generate_static_index_html'%time.ctime())
    # 2.获取频道和分类
    categories = get_categories()
    # 3.获取广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 4.渲染模板
    context = {
        'categories':categories,
        'contents':contents
    }
    # 5.获取首页模板文件
    template = loader.get_template('index.html')
    # 6.渲染首页html字符串(获取数据)
    html_text = template.render(context)
    #将首页的html字符串写入到制定目录,命名'index.html'
    file_path = os.path.join(settings.STATICFILES_DIRS[0],'index.html')
    with open(file_path,'w',encoding='utf-8') as f:
        f.write(html_text)