from django import http

from django.shortcuts import render

# Create your views here.

#商品列表页
from django.views import View

from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU
from apps.goods.utils import get_brandcrumb
from utils.response_code import RETCODE

"""
列表页面:
    有分类数据,面包屑(一级分类-->二级分类-->三级分类),列表数据,热销数据

    列表数据/热销数据其实是可以通过 ajax局部刷新的,但是由于我们讲的是前后端不分离
    所以我们把列表数据 放在我们查询之后,传递给模板,通过模板来渲染
"""
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
        sort = request.GET.get('sort','hot')
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

    """
    热销数据的获取

    需求:
        当用户点击了某一个分类之后,需要让前端将分类id传递给热销视图

    后端:

        1.根据分类查询数据,进行排序,排序之后获取2条数据
        2.热销数据在某一段时间内 很少变化 可以做缓存

        路由和请求方式

        GET     hot/category_id/
    """
#热销数据的获取
class HotView(View):
    def get(self,request,category_id):
        """
        1.根据分类查询数据,进行排序,排序之后获取2条数据
        2.热销数据在某一段时间内 很少变化 可以做缓存
        :param request:
        :param category_id:
        :return:
        """
        # 1.根据分类查询数据, 进行排序, 排序之后获取2条数据
        skus = SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]

        #2.热销数据在某一段时间内 很少变化 可以做缓存
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id':sku.id,
                'price':sku.price,
                'default_image_url':sku.default_image.url,
                'name':sku.name
            })
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','hot_skus':hot_skus})