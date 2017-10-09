from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ContractCreationView.as_view(), name='contract_creation'),
]