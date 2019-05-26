from django.conf.urls import url
from . import views


urlpatterns = [
    # OrderSettlementView
    url(r'^settlement/$', views.OrderSettlementView.as_view(), name='settlement'),

    # OrderCommitView
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='ordercommit'),

   ]
