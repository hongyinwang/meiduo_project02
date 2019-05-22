from django.shortcuts import render

# Create your views here.

#商品列表页
from django.views import View

from apps.contents.utils import get_categories


class ListView(View):
    def get(self,request,category_id):
        #1.获取分类数据
        categories= get_categories()
        #渲染模板的上下文
        context = {
            "categories":categories
        }
        return render(request,'list.html',context=context)