import json

from decimal import Decimal
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render

# Create your views here.
from django.utils import timezone

from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
import logging
logger = logging.getLogger('django')

#订单
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin

"""保存订单信息和订单商品信息"""
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
            sku.amount=sku.count*sku.price   #金额小计
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

#订单提交页面
class OrderCommitView(LoginRequiredJSONMixin, View):
    # 订单提交页面
    def post(self, request):
        """
    生成订单信息需要涉及到订单基本信息和订单商品信息,因为 订单基本信息订单商品信息
    是1对n,所以先生成1(订单基本信息)的数据,再生成订单商品

    # 1. 生成订单基本信息
    #     1.1获取用户信息(必须是登陆用户)
    #     1.2获取用户地址
    #     1.3获取用户的支付方式
    #     1.4手动生成订单号
    #     1.5获取运费总金额,总数量
    #     1.6订单状态(由支付方式决定)
    #     1.7支付方式
    #     1.8.保存订单信息(mysql数据库)
    # 2. 生成订单商品订单生成(简单)信息
    #     2.1 连接redis.获取redis中的数据
    #     2.2 获取选中商品的id [1,2,3]
    #     2.3 对id进行遍历
    #         2.4 查询商品
    #         2.5 库存量的判断
    #         2.6 修改商品的库存和销量
    #         2.7 累加总数量和总金额
    #         2.8 保存订单商品信息
    #         2.9 保存订单的总数量和总金额

    """
        # 1. 生成订单基本信息
        #     1.1获取用户信息(必须是登陆用户)
        user =request.user
        #     1.2获取提交的地址信息(id)
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
                #验证模型类中是否存在地址信息
        try:
            address = Address.objects.get(pk=address_id)
        except Address.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.PARAMERR,'errmsg':'参数错误'})
        #     1.3获取用户的支付方式
        pay_method =data.get('pay_method')
        #     判断前端传过来的支付方式是否在自己的模型库中
        if not pay_method in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})
        #     1.4手动生成一个订单id(年月日时分秒)+9位用户id
        from django.utils import timezone
        order_id=timezone.now().strftime('%Y%m%d%H%M%S')+ '%09d'%user.id
        #     1.5初始化运费总金额,总数量
        freight = Decimal('10.00')
        total_amount = Decimal('0')
        total_count = 0
        #     1.6订单状态(由支付方式决定)
        #     1.7支付方式
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            #货到付款
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        else:
            #支付宝
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']

        from django.db import transaction

        with transaction.atomic():
            #01创建事务回滚的点
            save_point = transaction.savepoint()

            try:
                #     1.8.保存订单信息(mysql数据库)
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_count,
                    total_amount=total_amount,
                    freight=freight,
                    pay_method=pay_method,
                    status=status
                )

            # 2. 生成订单商品信息
                # 2.1 从redis中读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                redis_carts = redis_conn.hgetall('carts_%s'%user.id)
                selected = redis_conn.smembers('selected_%s'%user.id)
                    #把二进制转化成python字典数据
                    #初始化一个字典
                selected_carts = {}
                #       #对selected_ids进行遍历追加,获取选中的商品信息转化成hash格式
                for sku_id in selected:
                        #hash格式 user.id{sku_id,count}
                        #set格式 user.id{sku_id,sku_id}
                    selected_carts[int(sku_id)]=int(redis_carts[sku_id])
                        #获取选中商品的所有id [1,2,3]
                sku_ids = selected_carts.keys()

                # 2.2遍历购物车中被勾选的商品信息
                for id in sku_ids:
                    # 查询商品信息
                    sku = SKU.objects.get(pk=id)
                    # 库存量的判断
                    sku_count = selected_carts[sku.id]
                    if sku.stock < sku_count:
                        #02出错就会滚
                        transaction.savepoint_rollback(save_point)
                        return http.JsonResponse({'code':RETCODE.STOCKERR,'errmsg':'库存不足'})

                    # 模拟延迟
                    # import time
                    # time.sleep(7)

                    # 悲观锁SKU减少库存，增加销量
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()


                    # 2.3保存订单商品信息 OrderGoods（多）
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price
                    )

                    # 2.5保存商品订单中总价和总数量
                    order.total_count+=sku_count
                    order.total_amount+=(sku.price * sku_count)


                # 2.6添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()

            except Exception as e:
                logger.error(e)
                # 事务回滚
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 提交订单成功，显式的提交一次事务
            transaction.savepoint_commit(save_point)

            # # 清除购物车中已结算的商品
            # pl = redis_conn.pipeline()
            # pl.hdel('carts_%s' % user.id, *selected)
            # pl.srem('selected_%s' % user.id, *selected)
            # pl.execute()

            # 响应提交订单结果
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok','order_id': order.order_id})
