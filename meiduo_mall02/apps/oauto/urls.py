from django.conf.urls import url
from . import views


urlpatterns = [
    # 定义用户注册页面
    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='qqurl'),

]
