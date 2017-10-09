from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.AccountInfoView.as_view(), name='account_info'),
]