from django import http

from django.shortcuts import render

# Create your views here.

#商品列表页
from django.views import View

from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU
from apps.goods.utils import get_brandcrumb


class ListView(View):
    def get(self,request,category_id,page_num):
        """
        #1.获取分类数据
        #2.获取面包屑数据
        #3.列表数据的获取
        #3.1获取列表中的所有数据
        #3.2分类
        #3.3排序
        #4.分页数据的获取
        #4.1创建分页器,根据分页进行排序
        #4.2获取每页商品的数据
        #4.3获取列表页总页数
        :param request:
        :param category_id:
        :param page_num:
        :return:
        """
        #1.获取分类数据
        categories= get_categories()
        #2.获取面包屑数据
        #   获取面包屑数据就是获取分类数据，当用户点击一个分类的时候就应该把该数据的分类ｉｄ传给我们
        try:
            #这里获取到的是三级分类
            category = GoodsCategory.objects.get(pk=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseBadRequest('分类错误')

        #因为面包屑数据多次用到，所以抽取一下
        breadcrumb= get_brandcrumb(category)

        #3.列表数据的获取
        #3.1获取列表中的所有数据
        #3.2分类
        #3.3排序
        #先获取查询字符串的数据
        sort = request.GET.get('sort','default')
        #然后根据查询字符串确定排序的字段
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'

        skus = SKU.objects.filter(category=category).order_by(sort_field)

        #４分页数据的获取
        from django.core.paginator import Paginator
        # 4.1创建分页器,根据分页进行排序
        piginator = Paginator(skus,5)
        # 4.2获取每页商品的数据
        try:
            #类型转化
            page_num = int(page_num)
            page_skus= piginator.page(page_num)
        except Exception as e:
            pass
        # 4.3获取列表页总页数
        total_page = piginator.num_pages

        #渲染模板的上下文
        context = {
            "categories":categories,
            "breadcrumb":breadcrumb,
            'page_skus':page_skus,
            'total_page':total_page,
            'sort':sort,
            'category':category,
            'page_num':page_num

        }
        return render(request,'list.html',context=context)