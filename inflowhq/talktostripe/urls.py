from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.BaseTalk.as_view(), name='base'),
]