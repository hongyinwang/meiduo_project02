from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.varifications.contents import SMS_CODE_EXPIRE_TIME, YUNTONGXUN_EXPIRE_TIME
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE

#1.导入logging
import logging
#2.创建(获取)日志实例
logger = logging.getLogger('django')

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

#短信验证码
class SMSCodeView(View):

    def get(self,request,mobile):
        """
            1.后端要接收数据
            2.验证数据　（比对　用户提交的验证码是否和redis中的一致）
            2.1链接redis
            2.2根据uuid获取验证码中的内容,怎么保存的怎么获取
            2.3redis中的图片验证码有可能过期，判断是否过期
            2.4　比对
            2.5删除redis中已经获取的uuit,提高用户的体验度
            3.先获取看有没有标记位
            4.生成短信验证码
            4.1.记录短信验证码到控制台
            5.通过链接redis,来创建管道实例
            5.1将redis请求加入队列
            5.2执行celery任务
            5.3改为celery发送短信
            5.4delay()参数同任务的参数
            :param request:
            :param mobile:
            :return:
        """
        #1.接收数据(uuid,image_code)
        params = request.GET
        uuid = params.get('image_code_id')#图片验证码的uuid
        text_client = params.get('image_code')#用户输入的图片验证码内容

        #2.验证数据　（比对　用户提交的验证码是否和redis中的一致）
        #2.1链接redis
        from django_redis import get_redis_connection

        #对外界资源进行异常捕获，提高代码的健壮性
        #外界资源：［redis mysql 读取文件］
        try:
            redis_conn = get_redis_connection('code')
            #2.2根据uuid获取验证码中的内容,怎么保存的怎么获取
            text_server = redis_conn.get('img_%s'%uuid)
            #2.3redis中的图片验证码有可能过期，判断是否过期
            if text_server is None:
                return http.HttpResponseBadRequest("图片验证码已过期")
            #2.4　比对
            if text_server.decode().lower() != text_client.lower():
                return http.HttpResponseBadRequest("图片验证码不一致")
            #删除redis中已经获取的uuit,提高用户的体验度
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest("数据库链接问题")

        #3.先获取看有没有标记位
        send_flag = redis_conn.get('send_flag_%s'%mobile)
        if send_flag is not None:
            return http.HttpResponseBadRequest('操作太频繁了，sms_code请稍等片刻')

        #4.生成短信验证码
        from random import randint
        #12345
        #123450
        sms_code = '%06d'%randint(0,999999)
        #4.1.记录短信验证码到控制台
        logger.info(sms_code)
        print(sms_code)

        # # 4.保存短信验证码
        # redis_conn.setex('sms_%s'%mobile,SMS_CODE_EXPIRE_TIME,sms_code)
        #
        # # 生成一个标记为１来记录表示该用户已经注册过了
        # redis_conn.setex('send_flag_%s'%mobile,60,1)

        #5.通过链接redis,来创建管道实例
        # 管道技术,通过减少客户端与服务端的来回tcp包的数量，来提高性能
        pl =redis_conn.pipeline()
        #5.1将redis指令缓存到管道中
        pl.setex('sms_%s' % mobile, SMS_CODE_EXPIRE_TIME, sms_code)
        #5.1+生成标记为１(表示已经发送了)
        pl.setex('send_flag_%s' % mobile, 60, 1)
        #5.2通过execute执行管道
        pl.execute()

        #发送短信验证码
        #参数１．给那个手机发送 2.data=[模板中的数据]　模板1中短信验证码的内容
        # CCP().send_template_sms(mobile,[sms_code,YUNTONGXUN_EXPIRE_TIME],1)
        #5.3改为celery发送短信
        from celery_tasks.sms.tasks import send_sms_code
        #5.4delay()参数同任务的参数
        send_sms_code.delay(mobile,sms_code)
        return http.JsonResponse({"code":RETCODE.OK})