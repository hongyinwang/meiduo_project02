import os

from alipay import AliPay
from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.orders.models import OrderInfo
from meiduo_mall02 import settings
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin


class PaymentView(LoginRequiredJSONMixin,View):

    def get(self,request,order_id):
        """
        #1.查看要支付的订单
        #2.创建支付宝对象
        #3.生成登陆支付宝链接
        #4.响应登陆支付宝链接
        :param request:
        :param order_id:
        :return:
        """
        # 1.查看要支付的订单
            #查询用户信息
        user = request.user
        # try:
        #     order =OrderInfo.objects.get(order_id=order_id,
        #                                  user=user,
        #                                  status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        # except OrderInfo.DoesNotExist:
        #     return http.HttpResponseBadRequest('订单信息错误')
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseBadRequest('订单信息错误')
        # 2.创建支付宝对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None, # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/app_private_key.pem'),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"keys/alipay_public_key.pem"),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )
        # 3.生成登陆支付宝链接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='美多商城%s'%order_id,
            return_url=settings.ALIPAY_RETURN_URL
        )
        # 4.响应登陆支付宝链接
        alipay_url = settings.ALIPAY_URL + '?' +order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
