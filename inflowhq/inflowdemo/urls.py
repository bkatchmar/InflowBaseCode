from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.DemoLoginView.as_view(), name='demo_home'),
    url(r'^gmail-overlay/', views.DemoLoginGmailOverlayView.as_view(), name='demo_home_gmail'),
]