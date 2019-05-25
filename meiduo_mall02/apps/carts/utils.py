"""
将抽象的问题具体化

需求:
    当用户登陆的时候,需要将cookie数据合并到reids中

    1.用户登陆的时候
    2.合并数据
    将cookie数据合并到reids中
    1.获取到cookie数据
    2.遍历cookie数据
    3.当前是以cookie为主,所以我们直接将cookie数据转换为hash, set(记录选中的和未选中的)

    4.连接redis 更新redis数据
    5.将cookie数据删除

"""
import base64
import pickle

from django_redis import get_redis_connection

#当用户登陆的时候,需要将cookie数据合并到reids中
def merge_cookie_to_redis(request,user,response):
    """
    需求:
    当用户登陆的时候,需要将cookie数据合并到reids中
    #1.获取cookie中的数据
    #2.将cookie数据转换为hash, set(记录选中的和未选中的)
    #2.1判断cookie是否存在
        #2.2存在解密出来
        #2.3准备redis中hash,set的存储格式
        #2.4遍历cookie数据,将cookie数据转换为hash, set(记录选中的和未选中的)
    #3.连接redis 更新redis数据
    #3.1更新hash中的数据
    #3.2选中的添加到set中的
    #3.3未选中的 ids 从选中的集合中移除
    #4.将cookie数据删除
    #5.cookie存在返回响应
    #6.不存在的返回响应
    :param request:
    :param user:
    :param response:
    :return:
    """
    # 1.获取到cookie数据
    carts=request.COOKIES.get('carts')

    # 2.将cookie数据转换为hash, set(记录选中的和未选中的)
    # 2.1判断cookie是否存在
    if carts is not None:
        #2.2存在解密出来
        cookie_cart=pickle.loads(base64.b64decode(carts))
        # cookie数据格式：{  1:{count:15,selected:True},
        #                  2:{count:200,selected:False} }

        #2.3准备redis中hash,set的存储格式
        # hash格式：{sku_id:count}
        cookie_hash={}
        #选中的id
        cookie_selected_ids=[]
        #未选中的id
        cookie_unselected_ids=[]
        #2.4遍历cookie数据,将cookie数据转换为hash, set(记录选中的和未选中的)
        for sku_id,count_selected_dict in cookie_cart.items():# 遍历出字典中所有的键值对(key-value)

            cookie_hash[sku_id]=count_selected_dict['count']

            if count_selected_dict['selected']:
                cookie_selected_ids.append(sku_id)
            else:
                cookie_unselected_ids.append(sku_id)

        # 3.连接redis 更新redis数据
        redis_conn = get_redis_connection('carts')
        # user=request.user
        #3.1更新hash中的数据
        redis_conn.hmset('carts_%s'%user.id,cookie_hash) #hash {sku_id:count}
        #3.2选中的添加到set中的
        if cookie_selected_ids:
            redis_conn.sadd('selected_%s'%user.id,*cookie_selected_ids)

        # 3.3未选中的 ids 从选中的集合中移除
        if cookie_unselected_ids:
            redis_conn.srem('selected_%s'%user.id,*cookie_unselected_ids)
        # 4.将cookie数据删除
        response.delete_cookie('carts')

        # 5.存在的返回响应
        return response

    #6.不存在的返回响应
    return response