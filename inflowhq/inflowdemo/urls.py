from django.conf.urls import url
from . import views

app_name = "htmldemos"
urlpatterns = [
    url(r'^$', views.DemoLoginView.as_view(), name='demo_home'),
    url(r'^welcome', views.DemoWelcome.as_view(), name='demo_welcome'),
    url(r'^address', views.DemoAddress.as_view(), name='demo_address'),
    url(r'^congratulations', views.DemoCongratulation.as_view(), name='demo_congratulation'),
    url(r'^stripe-connect', views.DemoStripeConnect.as_view(), name='demo_stripe_connect'),
    url(r'^stripe-thanks', views.DemoStripeThanks.as_view(), name='demo_stripe_thanks'),
    url(r'^terms-of-use', views.DemoTermsOfUse.as_view(), name='demo_tos'),
    url(r'^myprojects/create-contract/freelancer-msg', views.DemoCreateContractFreelancer.as_view(), name='demo_create_contract_freelancer'),
    url(r'^myprojects/create-contract/client-msg', views.DemoCreateContractClient.as_view(), name='demo_create_contract_client'),
    url(r'^myprojects/create-contract/received-email', views.DemoCreateContractReceivedEmail.as_view(), name='demo_create_contract_received_email'),
    url(r'^myprojects/create-contract/client-email-signed', views.DemoCreateContractClientEmailSigned.as_view(), name='demo_create_contract_client_email_signed'),
    url(r'^myprojects/create-contract/client-email-revision', views.DemoCreateContractClientEmailRevision.as_view(), name='demo_create_contract_client_email_revision'),
    url(r'^myprojects/create-contract/freelance-email-signed', views.DemoCreateContractFreelanceEmailSigned.as_view(), name='demo_create_contract_freelance_email_signed'),
    url(r'^myprojects/create-contract/freelance-email-revision', views.DemoCreateContractFreelanceEmailRevision.as_view(), name='demo_create_contract_freelance_email_revision'),
    url(r'^myprojects/project-details/', views.DemoProjectDetails.as_view(), name='demo_project_details'),
    url(r'^myprojects/create-contract/', views.DemoCreateNewContract.as_view(), name='demo_create_contract'),
    url(r'^myprojects/amend-contract/', views.DemoAmendContract.as_view(), name='demo_amend_contract'),
    url(r'^myprojects/upload-milestone/', views.DemoUploadMilestone.as_view(), name='demo_upload_milestone'),
    url(r'^myprojects/upload-milestone-drag/', views.DemoUploadMilestoneDrag.as_view(), name='demo_upload_milestone_drag'),
    url(r'^myprojects/preview-milestone/', views.DemoPreviewMilestone.as_view(), name='demo_preview_milestone'),
    url(r'^myprojects/', views.DemoMyProjectsScreen.as_view(), name='demo_my_projects'),
    url(r'^client-active-use/specific-project/milestones', views.ClientActiveUseLoFiSpecificProjectMilestone.as_view(), name='client_active_use_specific_project_milestones'),
    url(r'^client-active-use/specific-project/overview', views.ClientActiveUseLoFiSpecificProjectOverview.as_view(), name='client_active_use_specific_project_overview'),
    url(r'^client-active-use/quick-view', views.ClientActiveUseLoFiQuickView.as_view(), name='client_active_use_quick_view'),
    url(r'^client-active-use', views.ClientActiveUseLoFiHome.as_view(), name='client_active_use'),
]