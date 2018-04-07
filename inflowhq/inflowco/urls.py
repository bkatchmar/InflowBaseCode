from django.conf.urls import url
from . import views

app_name = "base"
urlpatterns = [
    url(r'^$', views.UserDashboardLowFi.as_view(), name='dashboard'),
    url(r'^help$', views.HelpCenter.as_view(), name='help_center'),
    url(r'^help/inflow-101$', views.HelpTopicInflow101.as_view(), name='help_topic_inflow_101'),
    url(r'^pdfview', views.SavePdfTrials.as_view(), name='mypdf'),
    url(r'^base-json', views.BasicJsonResponse.as_view(), name='bjson'),
    url(r'^model-json', views.DjangoModelJsonResponse.as_view(), name='mjson'),
]