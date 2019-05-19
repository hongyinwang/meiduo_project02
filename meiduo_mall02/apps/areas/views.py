from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from utils.response_code import RETCODE
from utils.views import LoginRequiredMixin
import logging

logger = logging.getLogger('django')

class AreasView(View):
    """省市区数据"""
    def get(self,request):
        """
        # 1.根据id获取省份数据
        # 1+判断省份id是否真实存在
        # 1++读取省份缓存数据
        # 2.查询省份数据
        # 3.序列化省份数据(把QuerySet转化成python列表形式)
        # 3++存储省份缓存数据
        # 4.响应省份数据
        :param request: 省市区数据
        :return: 省市区数据
        """
        # 1.根据id获取省份数据
        area_id = request.GET.get('area_id')

        # 1+判断省份id是否真实存在
        if not area_id:
            # 1++读取省份缓存数据
            provice_list = cache.get('province_list')

            if not provice_list:
                try:
                    # 2.再次查询省份数据
                    province_model_list = Area.objects.filter(parent__isnull=True)
                    # 3.序列化省份数据(把QuerySet转化成python列表形式)
                    provice_list = []
                    for province_model in province_model_list:
                        provice_list.append({'id':province_model.id,'name':province_model.name})
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({'code':RETCODE.DBERR,'errmsg':'省份数据错误'})

                    # 3++存储省份缓存数据
                cache.set('province_list',provice_list,3600)

                    # 4.响应省份数据
            return JsonResponse({'code':RETCODE.OK,'errmsg':'OK','provinces':provice_list})
        else:
            #1+读取市或者区的缓存
            sub_data = cache.get('sub_area_' + area_id)

            try:
                # 1.根据id获取市级数据
                parent_model = Area.objects.get(id=area_id)
                # 2.查询市或区数据
                sub_model_list = parent_model.subs.all()
                # 3.序列化省份数据(对获取到省份数据进行遍历,然后添加到列表中,转化成对象列表的形式)
                sub_list = []
                for sub_model in sub_model_list:
                    sub_list.append({"id":sub_model.id,'name':sub_model.name})
                # 4.定义父级数据(和子级建立关联性)
                sub_data ={
                    'id':parent_model.id,
                    'name':parent_model.name,
                    'subs':sub_list
                }
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code':RETCODE.DBERR,'errmsg':'城市或区数据错误'})

            #存储市或区的缓存
            cache.set('sub_area_' + area_id,sub_data,3600)

                # 4.响应省份数据
        return JsonResponse({'code':RETCODE.OK,'errmsg':'OK','sub_data':sub_data})



