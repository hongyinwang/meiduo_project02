from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from libs.yuntongxun.sms import CCP


class ImageCodeView(View):

    def get(self,request,uuid):
        #1.接受这个uuid 已经获取了
        #生成图片验证码，和保存图片的内容
            #2.1生成图片验证码
        from libs.captcha.captcha import captcha
        text,image = captcha.generate_captcha()
            #2.2保存图片的内容redis
        #2.2.1链接redis
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        #2.2.2 保存数据
        # redis_conn.setex(key,expire,value)
        redis_conn.setex('img_%s'%uuid,120,text)
        return http.HttpResponse(image,content_type='image.jpeg')

class SMSCodeView(View):

    def get(self,request,mobile):
        #1.后端要接收数据
        params = request.GET
        uuid = params.get('image_code_id')#图片验证码的uuid
        text_client = params.get('image_code')#用户输入的图片验证码内容
        #2.验证数据　比对　用户提交的验证码是否和redis中的一致
        #2.1链接redis
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        #2.2根据uuid获取验证码中的内容,怎么保存的怎么获取
        text_server = redis_conn.get('img_%s'%uuid)
        #2.3redis中的图片验证码有可能过期，判断是否过期
        if text_server is None:
            return http.HttpResponseBadRequest("图片验证码已过期")
        #2.4　比对
        if text_server.decode().lower() != text_client.lower():
            return http.HttpResponseBadRequest("图片验证码不一致")
        #3.生成短信验证码
        from random import randint
        #12345
        #123450
        sms_code = '%06d'%randint(0,999999)
        # 4.保存短信验证码
        redis_conn.setex('sms_%s'%mobile,300,sms_code)
        #5.发送短信验证码
        #参数１．给那个手机发送 2.data=[模板中的数据]　模板1中短信验证码的内容
        CCP().send_template_sms(mobile,[sms_code,5],1)
        return http.JsonResponse({"code":0})