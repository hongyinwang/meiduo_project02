
"""
分析:
    方向一: 通过经验
    方向二: 看别的网站的类似的效果


需求:

   1. 未登录用户可以实现购物车的添加,也能够保存数据

        登陆用户可以实现购物车的添加

    2.未登录用户保存在哪里  浏览器 (cookie中)

        登录用户保存在哪里  服务器  数据库中
                                Redis(课程设计,真实实现)

    3. 未登录用户保存 商品id,商品数量,勾选状态
        cookie:
        key:value
        carts: { sku_id: {count:xxx,selected:True} }


        carts: {
                    1:{count:5,selected:True},
                    3:{count:15,selected:False},
                }

        登录用户保存 用户id,商品id,商品数量,勾选状态

            数据库 user_id,sku_id,count,selected

                     1      1       5   1
                     1      3       15  0
                     333    1       1   1
                     333    2       1   0



            Redis(课程设计,真实实现)
            Redis是保存在内存中,我们的原则是:尽量少的占用内存空间 (先实现功能)

                 user_id,sku_id,count,selected



            Hash
                user_id:
                        sku_id:count,
                        sku_id:count,

                1:
                  1:10


                  2:20


                2:
                  1:10


                  2:20
            Set
                user_id: [sku_id,sku_id] 选中的商品的id

                1:  [1]

                2:


    4. 对cookie数据进行加密处理

        1G=1024MB
        1M=1024KB
        1KB=1024B
        1B=8bytes

        1字节=8b
        b: 0/1

        A       0100    0001

        A   A   A
        0100    0001    0100    0001    0100    0001

        X   y z s
        010000      010100    000101    000001

"""
import base64
import json
import pickle

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from utils.response_code import RETCODE

#购物车
class CartsView(View):
    #添加购物车
    def post(self,request):
        """
            需求:
                当用户点击加入购物车的时候,需要让前端收集  sku_id,count,selected(可以不提交默认是True)
                因为请求的时候会携带用户信息(如果用户登陆)
            后端:
                # 1.获取用户数据(sku_id,count,selected)
                # 2.验证用户数据
                    # 2.1 商品id,个数必须传递
                    # 2.2 判断商品是否存在
                    # 2.3 判断商品的个数是否为整形
                    # 2.4 判断选中状态是否为bool值
                # 3.判断用户登陆状态
                    # 3.1  获取user信息
                    # 3.2  判断是否登陆
                # 4.登陆用户保存在redis
                    # 4.1 连接redis
                    # 4.2 保存数据
                        # 保存数据(user.id,sku_id,count)到hash
                        # 保存选中数据(user.id,sku_id)到set
                    # 4.3 返回响应
                # 5.未登录用户保存在cookie中
                    # 5.1 判断sku_id 是否存在于cookie_cart
                        # 判断cookie中数据是否存在
                            # 存在则解密
                            # 不存在则初始化字典
                        # 判断sku_id 是否存在于cookie_cart
                            # 存在则获取原数据,并数量累加
                    # 5.2 更新数据(存在/不存在)
                    # 5.3 加密cookie中的数据
                    # 5.4 保存用户信息
                        # 设置response
                        # 设置cookie
                    # 5.5.返回响应
            路由和请求方式
                POST        carts
        """
        # 1.接收用户数据
        data = json.loads(request.body.decode())
            # 1.1.获取数据(sku_id,count,selected)
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected',True)

        # 2.验证数据
            # 2.1 商品id,个数必须传递
        if not all([sku_id,count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不全'})
            # 2.2 判断商品是否存在
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'没有此商品'})
            # 2.3 判断商品的个数是否为整形
        try:
            count = int(count)
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})
            # 2.4 判断选中状态是否为bool值
        if not isinstance(selected,bool):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})

        # 3.判断用户登陆状态
            # 3.1获取user信息
            # 3.2判断是否登陆
        user = request.user
        if user.is_authenticated:
        # 4.登陆用户保存在redis
            # 4.1 连接redis
            redis_conn = get_redis_connection('carts')
            # 4.2 保存数据
                # 保存数据(user.id,sku_id,count)到hash
            redis_conn.hincrby('carts_%s'%user.id,sku_id,count)
                # 保存选中数据(user.id,sku_id)到set
            redis_conn.sadd('selected_%s'%user.id,sku_id)
            # 4.3 返回响应
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

        # 5.未登录用户保存在cookie中
        else:
            # 5.1判断sku_id 是否存在于cookie_cart
                # 获取cookie中的数据
            carts = request.COOKIES.get('carts')
                # 判断cookie中数据是否存在
            if carts is not None:
                    # 存在则解密
                decode=base64.b64decode(carts)
                cookie_cart = pickle.loads(decode)
            else:
                    #不存在则初始化字典
                cookie_cart={}
                #判断sku_id是否存在于cookie_cart
            if sku_id in cookie_cart:
                    #存在则获取原数据,并数量累加
                orginal_count =cookie_cart[sku_id]['count']
                count += orginal_count
            #5.2更新数据(存在/不存在)
            cookie_cart[sku_id]={
                'count':count,
                'selected':selected
            }
            #5.3加密cookie中的数据
                    # 将字典转换为 bytes类型
            dumps = pickle.dumps(cookie_cart)
                    # 将bytes类型进行base64加密
            cookie_dumps = base64.b64encode(dumps)
            # 5.4保存用户信息
                # 设置response
            response = http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})
                # 设置cookie
            response.set_cookie('carts',cookie_dumps.decode(),max_age=3600)
            # 5.5返回响应
            return response

    #展示购物车
    def get(self,request):
        """
        #需求：
            当用户添加购物车完成后，需要将用户的购物车商品信息展示出来

        # 1.判断用户是否登陆
        # 2.登陆用户到redis中获取数据
        #   2.1 连接redis
        #   2.2 获取数据 hash   格式：carts_userid: {sku_id:count}
        #   2.3 获取数据 set     格式：set    selected: [sku_id,]
        #   2.4类型转换(将redis转换为cookie的格式)
        #       定义一个cookie形式字典
        #       拆包
        #       判断我们遍历的商品id,是否在选中的列表中
        # 3.未登录用户到cookie中获取数据
        #   3.1 获取cookie中carts数据,同时进行判断
        #       有数据
        #       没有数据
        # 4.获取所有商品的id
        #       获取sku对象
        #       将对象转换为字典
        # 5.组织响应数据
        # 6.返回响应
        :param request:
        :return:
        """
        # 1.判断用户是否登陆
        user = request.user
        if user.is_authenticated:
            # 2.登陆用户到redis中获取数据
            #     2.1 连接redis
            redis_conn = get_redis_connection('carts')
            #     2.2 获取数据 hash   格式：carts_userid: {sku_id:count}
            sku_id_count = redis_conn.hgetall('carts_%s' % user.id)
            #     2.3 获取数据 set     格式：set    selected: [sku_id,]
            selected_ids = redis_conn.smembers('selected_%s' % user.id)

            #   2.4类型转换(将redis转换为cookie的格式)
            # 因为 redis和cookie的数据格式不一致,我们需要转换数据,
            #   2.4.1定义一个cookie形式字典
            cookie_cart = {}
            #   2.4.2拆包
            for sku_id, count in sku_id_count.items():
                # 2.4.3判断我们遍历的商品id,是否在选中的列表中
                if sku_id in selected_ids:
                    selected = True
                else:
                    selected = False
                cookie_cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': selected
                }
        else:
            # 3.未登录用户到cookie中获取数据
            carts = request.COOKIES.get('carts')
            #     3.1 获取cookie中carts数据,同时进行判断
            if carts is not None:
                # 有数据
                decode = base64.b64decode(carts)
                cookie_cart = pickle.loads(decode)
            else:
                # 没有数据
                cookie_cart = {}

        # 4.获取所有商品的id
        ids = cookie_cart.keys()
        # 4.1 根据商品id查询商品的详细信息
        # mysql: float,double,decimal(货比类型)
        skus = []
        for id in ids:
            # 获取sku对象
            sku = SKU.objects.get(pk=id)
            # 将对象转换为字典
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cookie_cart.get(sku.id).get('count'),
                'selected': str(cookie_cart.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * cookie_cart.get(sku.id).get('count')),
            })
        #5.组织响应数据
        context = {
            'cart_skus': skus
        }
        #6.返回响应
        return render(request, 'cart.html', context)

    #修改购物车
    def put(self,request):
        """
        需求：
            在购物车页面修改购物车使用局部刷新的效果

        # 1.接收数据
        # 2.验证数据
        #     2.0 sku_id,selected,count 都要提交过来
        #     2.1 验证商品id
        #     2.2 验证商品数量
        #     2.3 验证选中状态是否为bool
        # 3.获取用户用户信息,根据用户信息进行判断
        # 4.登陆用户redis
        #     4.1 连接redis
        #     4.2 更新数据
        #     4.3 返回相应
        # 5.未登录用户cookie
        #     5.1 获取cookie中的carts数据
        #     5.2 判断数据是否存在
        #     5.3 更新数据
        #     5.4 对新数据进行加密处理
        #     5.5 返回相应
        :param request:
        :return:
        """

        # 1.接收数据
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected',True)

        # 2.验证数据
        #     2.0 sku_id,selected,count 都要提交过来
        if not all([sku_id,count,selected]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不全'})
        #     2.1 验证商品id
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '没有此商品'})
        #     2.2 验证商品数量
        try:
            count = int(count)
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})
        #     2.3 验证选中状态是否为bool
        if not isinstance(selected,bool):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})
        # 3.获取用户用户信息,根据用户信息进行判断
        user = request.user
        # 4.登陆用户redis
        if user.is_authenticated:
        #     4.1 连接redis
            redis_conn = get_redis_connection('carts')
        #     4.2 更新数据
            #hash
            redis_conn.hset('carts_%s'%user.id,sku_id,count)
            #set
            if selected:
                redis_conn.sadd('selected_%s'%user.id,sku_id)
            else:
                redis_conn.srem('selected_%s'%user.id,sku_id)
        #     4.3 返回相应
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_sku': cart_sku})
        # 5.未登录用户cookie
        else:
            #     5.1 获取cookie中的carts数据
            carts = request.COOKIES.get('carts')
            #     5.2 判断数据是否存在
            if carts is not None:
                cookie_cart = pickle.loads(base64.b64decode(carts))
            else:
                # 不存在
                cookie_cart = {}
            #     5.3 更新数据
            # {sku_id:{count:xxx,selected:xxxx}}
            if sku_id in cookie_cart:
                cookie_cart[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            #     5.4 对新数据进行加密处理
                cookie_data = base64.b64encode(pickle.dumps(cookie_cart))
            #     5.5 返回相应
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_sku': cart_sku})

            response.set_cookie('carts', cookie_data.decode(), 3600)

            return response

    #删除购物车
    def delete(self, request):
        """
            需求：
                在购物车页面删除购物车使用局部刷新的效果

           1.接收数据(sku_id)
           2.验证数据(验证商品是否存在)
           3.获取用户信息
           4.登陆用户操作redis
               4.1 连接redis
               4.2 删除数据 hash,set
               4.3 返回相应
           5.未登录用户操作cookie
               5.1 获取carts数据
               5.2 判断数据是否存在
               5.3 删除数据
               5.4 对最新的数据进行加密处理
               5.5 返回相应
           """
        # 1.接收数据(sku_id)
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        # 2.验证数据(验证商品是否存在)
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '无此数据'})
        # 3.获取用户信息
        user = request.user
        if user.is_authenticated:
            # 4.登陆用户操作redis
            #     4.1 连接redis
            redis_conn = get_redis_connection('carts')
            #     4.2 删除数据 hash,set
            # hash
            redis_conn.hdel('carts_%s' % user.id, sku_id)
            # set
            redis_conn.srem('selected_%s' % user.id, sku_id)
            #     4.3 返回相应
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

        else:
            # 5.未登录用户操作cookie
            #     5.1 获取carts数据
            carts = request.COOKIES.get('carts')
            #     5.2 判断数据是否存在
            if carts is not None:
                # 有数据
                cookie_cart = pickle.loads(base64.b64decode(carts))
            else:
                # 没有数据
                cookie_cart = {}
            # 5.3 删除数据
            if sku_id in cookie_cart:
                del cookie_cart[sku_id]
            # 5.4 对最新的数据进行加密处理
            cookie_data = base64.b64encode(pickle.dumps(cookie_cart))
            #     5.5 返回相应
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

            response.set_cookie('carts', cookie_data, 3600)

            return response
