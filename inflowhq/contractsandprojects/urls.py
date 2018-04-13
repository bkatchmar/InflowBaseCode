from django.conf.urls import url
from . import views

app_name = "contracts"
urlpatterns = [
    url(r'^$', views.ContractCreationView.as_view(), name='home'),
    url(r'^my-contacts$', views.MyContactsView.as_view(), name='my_contacts'),
    url(r'^contract/create/edit-(?P<contract_id>[0-9]+)', views.CreateContractStepOne.as_view(), name='create_contract_step_1_edit'),
    url(r'^contract/create', views.CreateContractStepOne.as_view(), name='create_contract_step_1'),
    url(r'^emailer', views.EmailPlaceholderView.as_view(), name='contract_email_placeholder'),
]