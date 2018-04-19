from django.conf.urls import url
from . import views

app_name = "contracts"
urlpatterns = [
    url(r'^$', views.ContractCreationView.as_view(), name='home'),
    url(r'^my-contacts$', views.MyContactsView.as_view(), name='my_contacts'),
    url(r'^contract/edit/(?P<contract_id>[0-9]+)', views.CreateContractStepOne.as_view(), name='create_contract_step_1_edit'),
    url(r'^contract/create/step-2/(?P<contract_id>[0-9]+)', views.CreateContractStepTwo.as_view(), name='create_contract_step_2'),
    url(r'^contract/create/step-3/(?P<contract_id>[0-9]+)', views.CreateContractStepThree.as_view(), name='create_contract_step_3'),
    url(r'^contract/create/step-4/(?P<contract_id>[0-9]+)', views.CreateContractStepFourth.as_view(), name='create_contract_step_4'),
    url(r'^contract/create/step-5/(?P<contract_id>[0-9]+)', views.CreateContractStepFive.as_view(), name='create_contract_step_5'),
    url(r'^contract/create', views.CreateContractStepOne.as_view(), name='create_contract_step_1'),
    url(r'^emailer', views.EmailPlaceholderView.as_view(), name='contract_email_placeholder'),
]