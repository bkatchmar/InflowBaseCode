from django.conf.urls import url
from . import views

app_name = "base"
urlpatterns = [
    url(r'^$', views.UserDashboardLowFi.as_view(), name='dashboard'),
    url(r'^pdfview', views.SavePdfTrials.as_view(), name='mypdf'),
    url(r'^base-json', views.BasicJsonResponse.as_view(), name='bjson'),
    url(r'^model-json', views.DjangoModelJsonResponse.as_view(), name='mjson'),
]