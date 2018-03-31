from django.conf.urls import url
from django.urls import path
from . import views

app_name = "htmldemos"
urlpatterns = [
    url(r'^$', views.DemoLoginView.as_view(), name='demo_home'),
    url(r'^myprojects/create-contract/', views.DemoCreateNewContract.as_view(), name='demo_create_contract'),
    url(r'^myprojects/upload-milestone', views.DemoUploadMilestone.as_view(), name='demo_upload_milestone'),
    url(r'^myprojects/upload-milestone-drag/', views.DemoUploadMilestoneDrag.as_view(), name='demo_upload_milestone_drag'),
    url(r'^freelancer-active-use/specific-project/milestones/upload-idle', views.FreelancerActiveUseLoFiSpecificProjectMilestoneUploadIdle.as_view(), name='freelancer_active_use_specific_project_milestones_upload_idle'),
    url(r'^freelancer-active-use/specific-project/milestones/upload-progress', views.FreelancerActiveUseLoFiSpecificProjectMilestoneUploadProgress.as_view(), name='freelancer_active_use_specific_project_milestones_upload_progress'),
    url(r'^freelancer-active-use/specific-project/milestones/preview/note', views.FreelancerActiveUseLoFiSpecificProjectMilestonePreviewNote.as_view(), name='freelancer_active_use_specific_project_milestones_preview_note'),
    url(r'^freelancer-active-use/specific-project/milestones/preview', views.FreelancerActiveUseLoFiSpecificProjectMilestonePreview.as_view(), name='freelancer_active_use_specific_project_milestones_preview'),
    url(r'^freelancer-active-use/specific-project/milestones/schedule/confirm-now', views.FreelancerActiveUseLoFiSpecificProjectMilestoneScheduleDeliveryConfirmSendNow.as_view(), name='freelancer_active_use_specific_project_milestones_schedule_send_now'),
    url(r'^freelancer-active-use/specific-project/milestones/schedule/confirm', views.FreelancerActiveUseLoFiSpecificProjectMilestoneScheduleDeliveryConfirmSend.as_view(), name='freelancer_active_use_specific_project_milestones_schedule_send'),
    url(r'^freelancer-active-use/specific-project/milestones/schedule', views.FreelancerActiveUseLoFiSpecificProjectMilestoneScheduleDelivery.as_view(), name='freelancer_active_use_specific_project_milestones_schedule'),
    url(r'^freelancer-active-use/specific-project/milestones', views.FreelancerActiveUseLoFiSpecificProjectMilestone.as_view(), name='freelancer_active_use_specific_project_milestones'),
    url(r'^freelancer-active-use/specific-project/overview', views.FreelancerActiveUseLoFiSpecificProjectOverview.as_view(), name='freelancer_active_use_specific_project_overview'),
    url(r'^freelancer-active-use/specific-project/invoices', views.FreelancerActiveUseLoFiSpecificProjectInvoices.as_view(), name='freelancer_active_use_specific_project_invoices'),
    url(r'^freelancer-active-use/specific-project/files', views.FreelancerActiveUseLoFiSpecificProjectFiles.as_view(), name='freelancer_active_use_specific_project_files'),
    url(r'^freelancer-active-use/quick-view', views.FreelancerActiveUseLoFiQuickView.as_view(), name='freelancer_active_use_quick_view'),
    url(r'^freelancer-active-use/email-confirm/freelancer', views.FreelancerActiveUseLoFiSpecificProjectEmailConfirmFreelancer.as_view(), name='freelancer_active_use_email_confirm_freelancer'),
    url(r'^freelancer-active-use/email-confirm/client', views.FreelancerActiveUseLoFiSpecificProjectEmailConfirmClient.as_view(), name='freelancer_active_use_email_confirm_client'),
    url(r'^freelancer-active-use', views.FreelancerActiveUseLoFiHome.as_view(), name='freelancer_active_use'),
    url(r'^client-active-use/projects-home/preview/accept/send', views.ClientActiveUseLoFiSpecificProjectMilestoneAcceptConfirmSend.as_view(), name='client_active_use_projects_preview_accept_send'),
    url(r'^client-active-use/projects-home/preview/accept', views.ClientActiveUseLoFiSpecificProjectMilestoneAccept.as_view(), name='client_active_use_projects_preview_accept'),
    url(r'^client-active-use/projects-home/preview/decline/send', views.ClientActiveUseLoFiSpecificProjectMilestonePreviewDeclineSend.as_view(), name='client_active_use_projects_preview_decline_send'),
    url(r'^client-active-use/projects-home/preview/decline', views.ClientActiveUseLoFiSpecificProjectMilestonePreviewDecline.as_view(), name='client_active_use_projects_preview_decline'),
    url(r'^client-active-use/projects-home/preview', views.ClientActiveUseLoFiSpecificProjectMilestonePreview.as_view(), name='client_active_use_projects_preview'),
    url(r'^client-active-use/projects-home/files', views.ClientActiveUseLoFiSpecificProjectFiles.as_view(), name='client_active_use_projects_files'),
    url(r'^client-active-use/projects-home/invoices', views.ClientActiveUseLoFiSpecificProjectInvoices.as_view(), name='client_active_use_projects_invoices'),
    url(r'^client-active-use/projects-home/overview', views.ClientActiveUseLoFiSpecificProjectOverview.as_view(), name='client_active_use_projects_overview'),
    url(r'^client-active-use/projects-home/milestones', views.ClientActiveUseLoFiSpecificProjectMilestone.as_view(), name='client_active_use_projects_milestones'),
    url(r'^client-active-use/projects-home/quick-view', views.ClientActiveUseLoFiQuickView.as_view(), name='client_active_use_projects_quick_view'),
    url(r'^client-active-use/projects-home', views.ClientActiveUseLoFiProjectsHome.as_view(), name='client_active_use_projects_home'),
    url(r'^client-active-use', views.ClientActiveUseLoFiHome.as_view(), name='client_active_use'),
    url(r'^contract-creation/step-2/lump-sum', views.CreateContractStepTwoLumpSum.as_view(), name='contract_creation_lump_sum'),
    url(r'^contract-creation/step-2/hourly', views.CreateContractStepTwoHourly.as_view(), name='contract_creation_hourly'),
    url(r'^contract-creation/step-3', views.CreateContractStepThreeHourly.as_view(), name='contract_creation_extra_fees'),
    url(r'^contract-creation/step-4/lump-sum', views.CreateContractStepFourLumpSum.as_view(), name='contract_overview_lump_sum'),
    url(r'^contract-creation/step-4/hourly', views.CreateContractStepFourHourly.as_view(), name='contract_overview_hourly'),
    url(r'^contract-creation/step-5', views.CreateContractStepFive.as_view(), name='contract_overview_preview_send'),
    url(r'^contract-creation/final', views.CreateContractCongrats.as_view(), name='contract_overview_final'),
    url(r'^contract-creation', views.CreateContractStepOneDemo.as_view(), name='contract_creation'),
    url(r'^contract-review/lump-sum/edit', views.CreateContractStepFourLumpSumEdit.as_view(), name='contract_overview_lump_sum_edit'),
    url(r'^contract-review/hourly/edit', views.CreateContractStepFourHourlyEdit.as_view(), name='contract_overview_hourly_edit'),
    url(r'^contract-review/making-edit', views.ReviewMakingEdit.as_view(), name='contract_review_making_edit'),
]