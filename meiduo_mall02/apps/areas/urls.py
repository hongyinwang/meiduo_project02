from django.conf.urls import url
from . import views


urlpatterns = [
    # 定义用户注册页面
    url(r'^areas/$', views.AreasView.as_view(), name='areas'),

]
