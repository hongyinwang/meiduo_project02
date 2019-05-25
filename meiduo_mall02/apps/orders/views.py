from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.users.models import Address


#订单
class OrderSettlementView(LoginRequiredMixin,View):
    #订单结算
    def get(self,request):
        """
        需求:订单结算页面的展示

        1.这个界面必须是登陆用户
        2.获取用户信息,
        3.根据用户信息,获取地址信息
        4.连接redis,获取redis中的 hash和set数据
            hash:
            set:
        5.将bytes数据类型进行转换,转换的同时我们重新组织选中的商品数据
            只有选中的 {sku_id:count}
        6.获取商品的id,根据商品id查询商品信息 [sku,sku]
        7.对商品列表进行遍历
        8.遍历的过程中 对sku添加数量和对应商品的总金额
            也去计算当前订单的总数量和总金额
        9.再添加一个运费信息
        10.组织渲染数据
        """

        # 1.这个界面必须是登陆用户
        # 2.获取用户信息
        user=request.user
        # 3.根据用户信息,获取地址信息
        try:
            addresses=Address.objects.filter(user=user,is_deleted=False)
        except Exception as e:
            return http.HttpResponseNotFound('未找到数据')
        # 4.连接redis,获取redis中的 hash和set数据
        redis_conn = get_redis_connection('carts')
        #     hash  {sku_id:count}
        sku_id_count=redis_conn.hgetall('carts_%s'%user.id)
        #     set:
        ids=redis_conn.smembers('selected_%s'%user.id)

        # 5.将bytes数据类型进行转换,转换的同时我们重新组织选中的商品数据
        #     只有选中的 {sku_id:count}
        selected_carts={}
        for id in ids:
            selected_carts[int(id)]=int(sku_id_count[id])

        # 6.获取商品的id,根据商品id查询商品信息 [sku,sku]
        ids=selected_carts.keys()
        # [1,2,3]
        skus=SKU.objects.filter(pk__in=ids)
        # 7.对商品列表进行遍历
        total_count=0 #总数量
        from decimal import Decimal
        total_amount=Decimal('0') #总金额
        # 0.233333 小数是以无限接近于真实值形式存在的
        # 1000 / 3      333.33
        # 333.33*3 = 999.99
        # 333.33  333.33    333.34
        for sku in skus:
            # 8.遍历的过程中 对sku添加数量和对应商品的总金额
            sku.count=selected_carts[sku.id] #数量小计
            sku.amount=sku.count*sku.price                   #金额小计
            #     也去计算当前订单的总数量和总金额
            total_count += sku.count
            total_amount += sku.amount

        #9.再添加一个运费信息
        freight=Decimal('10.00')
        #10.组织渲染数据
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        #11.返回响应
        return render(request, 'place_order.html', context=context)

