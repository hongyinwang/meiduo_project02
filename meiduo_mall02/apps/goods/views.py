from django import http
from django.shortcuts import render

# Create your views here.

#商品列表页
from django.views import View

from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory
from apps.goods.utils import get_brandcrumb


class ListView(View):
    def get(self,request,category_id):
        #1.获取分类数据
        categories= get_categories()
        #2.获取面包屑数据
        #   获取面包屑数据就是获取分类数据，当用户点击一个分类的时候就应该把该数据的分类ｉｄ传给我们
        try:
            category = GoodsCategory.objects.get(pk=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseBadRequest('分类错误')

        #因为面包屑数据多次用到，所以抽取一下
        breadcrumb= get_brandcrumb(category)

        #渲染模板的上下文
        context = {
            "categories":categories,
            "breadcrumb":breadcrumb
        }
        return render(request,'list.html',context=context)