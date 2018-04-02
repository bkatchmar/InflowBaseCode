from django.conf.urls import url
from . import views

app_name = "contracts"
urlpatterns = [
    url(r'^$', views.ContractCreationView.as_view(), name='home'),
    url(r'^emailer/', views.EmailPlaceholderView.as_view(), name='contract_email_placeholder'),
]