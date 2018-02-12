from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^currencies/', views.CurrencyListView.as_view(), name='currencylistview'),
    url(r'^linkedinhandler/', views.LinkedInHandler.as_view(), name='linkedin'),
    url(r'^amazonboto/', views.AmazonBotoExamples.as_view(), name='amazonboto'),
    url(r'^googlehandler/', views.GoogleHandler.as_view(), name='gmail'),
    url(r'^pdfview/', views.SavePdfTrials.as_view(), name='mypdf'),
]