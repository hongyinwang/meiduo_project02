from django.conf.urls import url
from . import views


urlpatterns = [
    # 定义用户注册页面
    url(r'^register/$', views.RegisterView.as_view(), name='register'),

    # 校验用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/$', views.UsernameCountView.as_view(), name='usernamecount'),

    #LoginView
    url(r'^loginview/$', views.LoginView.as_view(), name='loginview'),

    #LogoutView
    url(r'^logoutview/$', views.LogoutView.as_view(), name='logoutview'),

    #UserCenterInfo
    url(r'^info/$', views.UserCenterInfo.as_view(), name='info'),

    #UserCenterInfo
    url(r'^emails/$', views.EmailView.as_view(), name='emails'),

    #VerifyEmailView
    url(r'^emails/verification/$', views.VerifyEmailView.as_view(), name='emails'),

    # AddressView
    url(r'^address/$',views.AddressView.as_view(), name='address'),

    # CreateAddressView
    url(r'^addresses/create/$',views.CreateAddressView.as_view(), name='createaddress'),

    # UpdateDestroyAddressView
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(), name='updateaddress'),

    # DefaultAddressView
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name='defaultaddress'),

    # UpdateTitleAddressView
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(), name='updatetitle'),
]
