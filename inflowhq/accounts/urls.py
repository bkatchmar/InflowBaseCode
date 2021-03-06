from django.conf.urls import url
from . import views

app_name = "accounts"
urlpatterns = [
    url(r'^login$', views.AccountLoginView.as_view(), name='login'),
    url(r'^create/onboarding-1', views.OnboardingStepOneView.as_view(), name='onboarding_1'),
    url(r'^create/onboarding-2', views.OnboardingStepTwoView.as_view(), name='onboarding_2'),
    url(r'^create/onboarding-3', views.OnboardingStepThreeView.as_view(), name='onboarding_3'),
    url(r'^create', views.CreateAccountView.as_view(), name='create'),
    url(r'^settings', views.EditProfileView.as_view(), name='settings'),
    url(r'^edit-account', views.EditAccountView.as_view(), name='edit_account'),
    url(r'^notifications', views.EditNotificationsView.as_view(), name='notifications'),
    url(r'^invitation/(?P<invitation_guid>[-\w]+)', views.AccountInvitationView.as_view(), name='invitation'),
]