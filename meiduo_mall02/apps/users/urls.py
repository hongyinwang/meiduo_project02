from django.conf.urls import url
from . import views


urlpatterns = [
    # 定义用户注册页面
    url(r'^register/$', views.RegisterView.as_view(), name='register'),

    # 校验用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/',views.UsernameCountView.as_view(), name='usernamecount'),

    #LoginView
    url(r'^loginview',views.LoginView.as_view(),name='loginview')

]