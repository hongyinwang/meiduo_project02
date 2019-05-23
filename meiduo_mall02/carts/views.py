
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

from django.shortcuts import render

# Create your views here.
from django.views import View

class CartsView(View):
    """
    添加购物车的思路

        需求:
            当用户点击加入购物车的时候,需要让前端收集  sku_id,count,selected(可以不提交默认是True)
            因为请求的时候会携带用户信息(如果用户登陆)
        后端:

            # 1.后端接收数据
            # 2.验证数据
            # 3.判断用户登陆状态
            # 4.登陆用户保存在redis
            #     4.1 连接redis
            #     4.2 hash
            #         set
            #     4.3 返回
            # 5.未登录用户保存在cookie中
            #     5.1 组织数据
            #     5.2 加密
            #     5.3 设置cookie
            #     5.4 返回相应

        路由和请求方式
            POST        carts
    """
    def post(self,request):
        # 1.后端接收数据
        # 2.验证数据
        # 3.判断用户登陆状态
        # 4.登陆用户保存在redis
        #     4.1 连接redis
        #     4.2 hash
        #         set
        #     4.3 返回
        # 5.未登录用户保存在cookie中
        #     5.1 组织数据
        #     5.2 加密
        #     5.3 设置cookie
        #     5.4 返回相应

        pass