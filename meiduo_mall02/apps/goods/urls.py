from django.conf.urls import url
from . import views


urlpatterns = [
    # 定义用户注册页面
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),
    #HotView
    url(r'^hot/(?P<category_id>\d+)/$', views.HotView.as_view(), name='hot'),
    #DetailView
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),
    #DetailVisitView
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view(), name='visit'),

   ]
