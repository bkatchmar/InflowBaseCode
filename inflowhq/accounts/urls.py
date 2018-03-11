from django.conf.urls import url
from . import views

app_name = "accounts"
urlpatterns = [
    url(r'^login$', views.AccountLoginView.as_view(), name='login'),
    url(r'^create/onboarding-1', views.OnboardingStepOneView.as_view(), name='onboarding_1'),
    url(r'^create/onboarding-2', views.OnboardingStepTwoView.as_view(), name='onboarding_2'),
    url(r'^create/onboarding-3', views.OnboardingStepThreeView.as_view(), name='onboarding_3'),
    url(r'^create', views.CreateAccountView.as_view(), name='create'),
]