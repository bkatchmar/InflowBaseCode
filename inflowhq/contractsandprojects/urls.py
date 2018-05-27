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
    url(r'^contract/create/final/(?P<contract_id>[0-9]+)', views.ContractDoneCreated.as_view(), name='create_contract_step_6'),
    url(r'^contract/create', views.CreateContractStepOne.as_view(), name='create_contract_step_1'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/milestones/send-now/(?P<milestone_id>[0-9]+)', views.SendMilestoneNowConfirm.as_view(), name='project_milestone_send_confirm'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/milestones/confirm-schedule/(?P<milestone_id>[0-9]+)', views.ScheduleSendMilestoneConfirm.as_view(), name='project_milestone_schedule_confirm'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/milestones/schedule/(?P<milestone_id>[0-9]+)', views.ScheduleSendMilestone.as_view(), name='project_milestone_schedule'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/milestones/preview/(?P<milestone_id>[0-9]+)', views.PreviewMilestone.as_view(), name='project_milestone_preview'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/milestones', views.SpecificProjectMilestones.as_view(), name='project_milestones'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/invoices', views.SpecificProjectInvoices.as_view(), name='project_invoices'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/files', views.SpecificProjectFiles.as_view(), name='project_files'),
    url(r'^my-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/overview', views.SpecificProjectOverview.as_view(), name='project_overview'),
    url(r'^work-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/milestones', views.ClientSpecificProjectMilestones.as_view(), name='client_project_milestones'),
    url(r'^work-contract/(?P<contract_slug>[-\w]+)-(?P<contract_id>[0-9]+)/overview', views.ClientSpecificProjectOverview.as_view(), name='client_project_overview'),
    url(r'^emailer', views.EmailPlaceholderView.as_view(), name='contract_email_placeholder'),
    url(r'^contract-service/delete-milestone-file/(?P<milestone_file_id>[0-9]+)', views.JsonDeleteMilestoneFile.as_view(), name='json_delete_milestone_file'),
    url(r'^contract-service/delete-contract-file/(?P<contract_file_id>[0-9]+)', views.JsonDeleteContractFile.as_view(), name='json_delete_contract_file'),
    url(r'^contract-service/schedule-milestone/(?P<milestone_id>[0-9]+)', views.JsonScheduleMilestone.as_view(), name='json_schedule_milestone'),
    url(r'^contract-service/milestones/(?P<contract_id>[0-9]+)', views.JsonGetContractMilestones.as_view(), name='json_get_milestones'),
]