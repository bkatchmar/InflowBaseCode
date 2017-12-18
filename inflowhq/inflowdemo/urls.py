from django.conf.urls import url
from . import views

app_name = "htmldemos"
urlpatterns = [
    url(r'^$', views.DemoLoginView.as_view(), name='demo_home'),
    url(r'^myprojects/create-contract/freelancer-msg', views.DemoCreateContractFreelancer.as_view(), name='demo_create_contract_freelancer'),
    url(r'^myprojects/create-contract/client-msg', views.DemoCreateContractClient.as_view(), name='demo_create_contract_freelancer'),
    url(r'^myprojects/create-contract/', views.DemoCreateNewContract.as_view(), name='demo_create_contract'),
    url(r'^myprojects/', views.DemoMyProjectsScreen.as_view(), name='demo_my_projects'),
]