import re
from django import http
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
# Create your views here.
from django_redis import get_redis_connection

from apps.carts.utils import merge_cookie_to_redis
from apps.goods.models import SKU
from apps.users.models import Address
from apps.users.models import User


#1.导入logging
import logging
#2.创建(获取)日志实例
from apps.users.utils import generate_verify_email_url, check_verify_email_token
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin

logger = logging.getLogger('django')

from django.db import DatabaseError
# Create your models here.

#定义用户注册页面



class RegisterView(View):
    """用户注册"""
    #get请求方式
    def get(self, request):
        """

        :param request:
        :return:
        """

        return render(request, 'register.html')

    # post请求方式
    def post(self,request):
        """

        :param request:
        :return:
        """
        # ①接收数据 request.POST
        data = request.POST
        # ②分别获取数据 username,password
        #接受参数
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        allow = data.get('allow')
        sms_code_client = data.get('sms_code')

        # 校验参数
        # 判断参数是否齐全
        if not all([username,password,password2,mobile,allow,sms_code_client]):
            return http.HttpResponseBadRequest("参数不全")
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')

        #8.1验证用户提交的验证码是否和redis中保存的图形验证码是否一致
        #8.11链接redis
        redis_conn = get_redis_connection('code')
        # 2.2通过手机号获取uuid中短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 2.3redis中的短信验证码有可能过期，判断是否过期
        if not sms_code_server:
            return http.HttpResponseBadRequest("短信验证码已过期")
        # 2.4　比对
        if sms_code_server.decode().lower() != sms_code_client.lower():
            return http.HttpResponseBadRequest("短信验证码不一致")


        #保存注册数据
        try:
            user = User.objects.create_user(
                username = username,
                password = password,
                mobile = mobile
            )
        except Exception as e:
            logger.error(e)
            return render(request,'register.html',context={'register_errmsg': '注册失败'})
        #状态保持
        login(request, user)
        return redirect(reverse("contents:Index"))
        # return http.HttpResponse('ok')

#判断username是否重复
class UsernameCountView(View):

    def get(self, request, username):
        #校验
        #用户名查询登录
        count = User.objects.filter(username=username).count()

        #返回相应对象
        #将数据转换为json字符串,返回的是json数据
        return http.JsonResponse({'count': count})

#登陆页面的实现
class LoginView(View):

    def get(self,request):
        """

        :param request:
        :return:
        """
        return render(request,'login.html')

    def post(self,request):
        """
        :param request:
        :return:
        1.接受用户输入数据
        2.校验数据
        2.1参数是否齐全
        2.2用户名是否符合规则
        2.3密码是否符合规则
        2.4用django自带的认证系统去认证用户输入的信息是否和数据库相对应
            返回user对象
        2.5判断user对象是否存在
            不存在则返回登陆页及相关信息
        2.6判断用户是否属于登陆状态
            不登陆则设置过期时间为０
            登陆则设置过期时间None(即当浏览器回话结束时过期)
        3.保持登陆状态
        3+获取next参数
            #判断next参数是否存在，存在则跳转
            #不存在跳转到首页成功
        4.再次判断是否选择记住登陆状态(设置cockie,目的是用浏览器记住用户信息)
            #未登陆则设置过期时间浏览器回话结束时
            #登陆则设置过期时间一周
        5.返回响应

        """
        #1.接受用户输入数据
        datas = request.POST
        username = datas.get('username')
        password = datas.get('password')
        remembered = datas.get('remembered')


        #2.校验数
        #2.1判断参数是否齐全
        if not all([username,password]):
            return http.HttpResponseBadRequest("参数不齐全")
        #2.2用户名是否符合规则(5-20个字符)
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        #2.3密码是否符合规则(8-20个数字)
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        #2.4用django自带的认证系统去认证用户输入的信息是否和数据库相对应
            #返回user对象
        from django.contrib.auth import authenticate
        user = authenticate(username=username,password=password)
        #2.5判断user对象是否存在
        if user is None:
            return render(request,'login.html',context={'login_error_password':'用户名或者密码错误'})
        #2.6判断用户是否属于登陆状态
            # 不登陆则设置过期时间为０
            # 登陆则设置过期时间None(即当浏览器回话结束时过期)
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        #3.保持登陆状态
        login(request, user)
        #3+获取next参数
            #判断next参数是否存在，存在则跳转
            #不存在跳转到首页成功
        next = request.GET.get('next')
        if next:
            return redirect(next)
        else:
            response = redirect(reverse('contents:Index'))

        #4.再次判断是否选择记住登陆状态(设置cockie,目的是用浏览器记住用户信息)
            #未登陆则设置过期时间浏览器回话结束时
            #登陆则设置过期时间一周
        if remembered != 'on':
            response.set_cookie('username',user.username,max_age=None)
        else:
            response.set_cookie('username', user.username, max_age=14*24*3600)

        # 在这里合并
        response = merge_cookie_to_redis(request, user, response)

        #5.返回相应
        return response

from django.contrib.auth import logout
#登出界面
class LogoutView(View):

    def get(self,request):
        # 调用系统的logout方法
        logout(request)
        # 根据username清除cookie信息，因为我们的首页是根据username来判断是否登陆的
        # 返回相应，设置cookie
        response = redirect(reverse('contents:Index'))
        response.delete_cookie('username')
        #返回相应
        return response

#用户中心页面
class UserCenterInfo(LoginRequiredMixin,View):
    def get(self,request):
        """
        1.提供个人信息
        2.返回响应
        :param request:
        :return:
        """
        #1.提供个人信息
        context = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active': request.user.email,

        }
        #2.返回响应
        return render(request,'user_center_info.html',context=context)

'''
LoginRequiredMixin 会进行一个重定向
我们这里是进行的loadsajax 请求,我们应该返回一个json数据
'''
#EmailView
class EmailView(LoginRequiredJSONMixin,View):
    """
        # 1.接受body数据
        # 1.1把接受的bytes===>json数据
        # 1.2把json转化为dict
        # 1.3获取数据
        # 2.验证数据
        # 2.1邮箱地址是否存在,符合规则
        # 3.更新数据(email数据)
        # 4+验证邮箱的后端实现(加密)
        # 4.发送激活邮件/异步发送邮件
        # 4.1准备发送邮箱数据(主题，消息，发件人，收件人(列表)，内容)
        # 4.2发送数据
        # 5.返回响应
    """
    def put(self,request):
        # 1接受body数据
        body_datas = request.body
        # 1.1把接受的bytes===>json数据
        json_datas = body_datas.decode()
        # 1.2把json转化为dict
        dict_datas= json.loads(json_datas)
        # 1.3获取数据
        email = dict_datas.get('email')

        # 2.验证数据
        # 2.1邮箱地址是否存在,符合规则
        if not email:
            return http.HttpResponseBadRequest('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseBadRequest('参数email有误')

        # 3.更新数据(email数据)
            #成功则保存
            #不成功则更新失败
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            # raise self.retry(exc=e, max_retries=3)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'更新失败'})

        # 4.发送激活邮件
        # 4.1准备发送邮箱数据(主题，消息，发件人，收件人(列表)，内容)
        # subject = '美多商城激活邮件'
        # message = ''
        # from_email = '美多商城<qi_rui_hua@163.com>'
        # recipient_list = [email]
        # html_message = "<a href='#'>有思路,不纠结</a>"
        #
        # # 4.2发送数据
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=from_email,
        #     recipient_list=recipient_list,
        #     html_message=html_message
        # )

        # 4.2改为celery发送数据
        # 异步发送验证邮件
        # 4+验证邮箱的后端实现(加密)
        # verify_url = '邮件验证链接'
        verify_url = generate_verify_email_url(request.user)
        #4.异步发送邮件验证
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)
        # 5.返回响应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})

#验证邮箱后端逻辑实现
class VerifyEmailView(View):
    """验证邮箱"""
    def get(self,request):
        """
        #1.接受参数(tocken)
        #2.校验参数
        #2.1判断参数(tocken)是否存在/过期
        #3通过check_verify_email_token方法获取对象
        #3.1判断获取对象是否为空
        #4.激活用户并保存(异常处理)
        #5.返回响应
        :param request:用户点击邮箱激活的链接地址发送的请求
        :return:返回的激活邮箱的验证结果
                返回用户中心页面
        """
        # 1.接受参数(tocken)
        token = request.GET.get('token')
        # 2.校验参数
        # 2.1判断参数(tocken)是否存在/过期
        if token is None:
            return http.HttpResponseBadRequest("缺少参数")
        # 3通过check_verify_email_token方法获取对象
        user = check_verify_email_token(token)
        # 3.1判断获取对象是否为空
        if not user:
            return http.HttpResponseBadRequest('用户不存在')
        # 4.激活用户并保存(异常处理)
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest('激活失败')
        # 5.返回响应
        return redirect(reverse('users:info'))

#收货地址界面
class AddressView(View):

    def get(self,request):
        """
        # 1.获取请求对象
        # 2.通过用户查询出地址
        # 3.序列化省份地址
        # 4.准备响应数据
        # 5.返回响应
        :param request:用户地址信息
        :return:展示地址show_add_site()
        """
        # 1.获取请求对象
        login_user = request.user
        # 2.通过用户查询出地址
        addresses = Address.objects.filter(user=login_user,is_deleted=False)
        # 3.序列化省份地址
        address_dict_list = []
        for address in addresses:
            address_dict={
                'id':address.id,
                'title':address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)
        # 4.准备响应数据
        context ={
            'default_address_id':login_user.default_address_id,
            'addresses':address_dict_list
        }
        # 5.返回响应
        return render(request,'user_center_site.html',context)

#实现新增地址后端逻辑
class CreateAddressView(LoginRequiredJSONMixin,View):
    """
    1.新增地址
    2.请求方式post
    """
    def post(self,request):
        """
        # 1.判断地址数量上限
        # 2.接受参数
        # 3.校验参数
        # 4.保存存数
        # 5.将新增的地址响应给前端实现局部刷新
        # 6.返回相应
        :param request:
        :return:
        """
        # 1.判断地址数量上限
        count = request.user.addresses.count()
        if count >= 20:
            return JsonResponse({'code':RETCODE.DBERR,"errmsg":'地址数量已达上限'})
        # 2.接受参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id =json_dict.get('city_id')
        district_id =json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 3.校验参数
        # 3.1判断数据是否齐全×

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        # 3.2判断mobile是否符合规则
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        # 3.３判断tel是否符合规则
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        # 3.2判断邮箱是否符合规则
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')

        # 4.保存存数
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id =city_id,
                district_id=district_id,
                place=place,
                mobile= mobile,
                tel=tel,
                email=email
            )
            # 4.1.设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR,'errmsg':'新增地址失败'})
        # 5.将新增的地址响应给前端实现局部刷新
        address_dict={
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email

        }
        # 6.返回相应
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address':address_dict})

#更新(修改和删除)地址的后端逻辑
class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """
            # 1.判断地址数量上限
            # 2.接受参数
            # 3.校验参数
            # 4.判断地址是否存在,并更新地址信息
            # 5.构造响应数据
            # 6.返回相应
        """
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user = request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """
        1.查询(根据地址id)要删除的地址
        2.将地址逻辑删除设置为True

        :param request:要删除的地址
        :param address_id:address_id
        :return:'errmsg': '删除地址成功'
        """
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})

#设置默认地址的后端逻辑
class DefaultAddressView(LoginRequiredJSONMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """
        1.查询(根据地址id)要设置的地址
        2.设置地址为默认地址
        :param request:点击设置默认来设置默认地址
        :param address_id:
        :return:'errmsg': '设置默认地址成功'
        """
        try:
            # 1.查询(根据地址id)要设置的地址
            address = Address.objects.get(id=address_id)

            # 2.设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        # 响应设置默认地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})

#修改地址标题的后端实现
class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """
        1.接受参数设置标题
        2.根据id查询出地址
        3.更新标题
        4.返回响应
        :param request: 设置地址标题
        :param address_id:
        :return:
        """
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})

#修改密码
class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """
        1.接受参数
        2.验证参数
        3.检查旧密码是否正确
        4.输入新密码
        5.退出登陆，删除登陆信息
        6.跳转到登陆页面
        :param request: 实现修改密码逻辑
        :return:
        """
        # 1.接收参数
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        # 2.验证参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseBadRequest('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')

        # 3.检验旧密码是否正确
        if not request.user.check_password(old_password):
            return render(request, 'user_center_pass.html', {'origin_password_errmsg':'原始密码错误'})
        # 4.更新新密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_password_errmsg': '修改密码失败'})
        # 5.退出登陆,删除登陆信息
        logout(request)
        # 6.跳转到登陆页面
        response = redirect(reverse('users:loginview'))

        response.delete_cookie('username')

        return response

    """
    添加用户浏览记录的
    需求

        当登陆用户访问某一个商品详情页面的时候,需要让前端发送一个ajax请求,将用户信息和sku_id
        发送给后端
     后端:

        1.接收数据
        2.判断验证数据
        3.数据入库(redis)
        4.返回相应

        请求方式和路由
        POST    browse_histories/
    """
#保存和查询浏览记录
class UserBrowseHistory(LoginRequiredMixin,View):

    def post(self,request):
        """
        # 1.接受数据(user_id,date,sku_id)
        # 2.通过sku_id获取对象中所有数据,在判断数据是否存在
        # 3.保存浏览数据
        # 3.1.链接数据库
        # 3.2创建管道实例
        # 3.3去重 [lrem(key,重复次数,value)]
        # 3.4存储
        # 3.5最后截取[ltrim(key,截取区间)]
        # 4.返回响应
        :param request: 访问详情页面
        :return: sku_id　用户信息
        """
        # 1.接受数据(user_id,sku_id)
        user_id = request.user.id
        date = json.loads(request.body.decode())
        sku_id = date.get('sku_id')#这里的sku_id是前端传过来的

        # 2.通过sku_id获取对象中所有数据,在判断数据是否存在
        try:
            SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseBadRequest('sku不存在')

        # 3.保存浏览数据
        # 3.1.链接数据库
        redis_conn = get_redis_connection('history')
        # 3.2创建管道实例
        pl = redis_conn.pipeline()
        # 3.3去重 [lrem(key,重复次数,value)]
        pl.lrem('history_%s'%user_id,0,sku_id)
        # 3.4存储
        pl.lpush('history_%s'%user_id,sku_id)
        # 3.5最后截取[ltrim(key,截取区间)]
        pl.ltrim('history_%s'%user_id,0,4)
        # 3.6执行
        pl.execute()
        # 4.返回响应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})

    def get(self,request):
        """
        # 1.获取用户对象(信息)
        # 1.1.链接redis,获取前五个用户浏览的sku_id
        # 1.2 遍历用户id来获取用户的详细信息
        # 1.2.1 定义一个商品表
        # 1.2.2 对sku_id进行遍历
        # 1.2.3 根据sku_id查询出产品的所有信息
        # 1.2.4 将对象转化为字典
        # 2.返回数据

        :param request:
        :return:
        """

        # 1.获取用户对象(信息)
        user = request.user
        # 1.1.链接redis,获取用户浏览的前五个sku_id
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % user.id, 0, 4)
        # 1.2 遍历用户id来获取用户的详细信息
        # 1.2.1 定义一个商品表
        skus = []
        # 1.2.2 对sku_id进行遍历
        for sku_id in sku_ids:
            # 1.2.3 根据sku_id查询出产品的所有信息
            sku = SKU.objects.get(id=sku_id)
            # 1.2.4 将对象转化为字典
            skus.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        # 2.返回数据
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok','skus':skus})


