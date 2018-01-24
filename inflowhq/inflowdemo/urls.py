from django.conf.urls import url
from . import views

app_name = "htmldemos"
urlpatterns = [
    url(r'^$', views.DemoLoginView.as_view(), name='demo_home'),
    url(r'^welcome', views.DemoWelcome.as_view(), name='demo_welcome'),
    url(r'^address', views.DemoAddress.as_view(), name='demo_address'),
    url(r'^congratulations', views.DemoCongratulation.as_view(), name='demo_congratulation'),
    url(r'^myprojects/create-contract/freelancer-msg', views.DemoCreateContractFreelancer.as_view(), name='demo_create_contract_freelancer'),
    url(r'^myprojects/create-contract/client-msg', views.DemoCreateContractClient.as_view(), name='demo_create_contract_client'),
    url(r'^myprojects/create-contract/received-email', views.DemoCreateContractReceivedEmail.as_view(), name='demo_create_contract_received_email'),
    url(r'^myprojects/create-contract/client-email-signed', views.DemoCreateContractClientEmailSigned.as_view(), name='demo_create_contract_client_email_signed'),
    url(r'^myprojects/create-contract/client-email-revision', views.DemoCreateContractClientEmailRevision.as_view(), name='demo_create_contract_client_email_revision'),
    url(r'^myprojects/create-contract/freelance-email-signed', views.DemoCreateContractFreelanceEmailSigned.as_view(), name='demo_create_contract_freelance_email_signed'),
    url(r'^myprojects/create-contract/freelance-email-revision', views.DemoCreateContractFreelanceEmailRevision.as_view(), name='demo_create_contract_freelance_email_revision'),
    url(r'^myprojects/create-contract/', views.DemoCreateNewContract.as_view(), name='demo_create_contract'),
    url(r'^myprojects/amend-contract/', views.DemoAmendContract.as_view(), name='demo_amend_contract'),
    url(r'^myprojects/', views.DemoMyProjectsScreen.as_view(), name='demo_my_projects'),
]
