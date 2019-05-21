from collections import OrderedDict

from django.shortcuts import redirect, render

# Create your views here.
from django.urls import reverse
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from apps.goods.models import GoodsChannel


# class Index(View):
#     def get(self,request):
#
#         return render(request,'index.html')


#查询首页频道分类
class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告界面"""
        #1.查询商品频道和分类
        categories = get_categories()

        #2.广告数据
        #2.1定义一个内容字典
        contents = {}
        #2.2获取所有的内容分类
        content_categories = ContentCategory.objects.all()
        #2.3遍历
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        #渲染模板的上下文
        context = {
            'categories': categories,
            'contents':contents,
        }
        return render(request, 'index.html', context)