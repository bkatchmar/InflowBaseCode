from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.BaseTalk.as_view(), name='base'),
    url(r'^stripe-setup/$', views.ConnectStripeToAccount.as_view(), name='connect'),
    url(r'^stripe-setup/result/$', views.StripeConnectResult.as_view(), name='connectresult'),
]