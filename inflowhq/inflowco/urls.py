from django.conf.urls import url
from . import views

app_name = "base"
urlpatterns = [
    url(r'^$', views.UserDashboardView.as_view(), name='dashboard'),
    url(r'^currencies', views.CurrencyListView.as_view(), name='currencylistview'),
    url(r'^amazonboto', views.AmazonBotoExamples.as_view(), name='amazonboto'),
    url(r'^pdfview', views.SavePdfTrials.as_view(), name='mypdf'),
]