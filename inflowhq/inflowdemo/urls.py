from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.DemoLoginView.as_view(), name='demo_home'),
    url(r'^myprojects/', views.DemoMyProjectsScreen.as_view(), name='demo_my_projects'),
]