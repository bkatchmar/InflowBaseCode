from django.conf.urls import url
from . import views

app_name = "accounts"
urlpatterns = [
    url(r'^$', views.AccountInfoView.as_view(), name='account_info'),
    url(r'^create/', views.CreateAccountView.as_view(), name='create'),
]