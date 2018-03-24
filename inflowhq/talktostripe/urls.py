from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.BaseTalk.as_view(), name='stripebasepoint'),
    url(r'^express-setup$', views.BaseExpressTalk.as_view(), name='stripe_express_setup'),
    url(r'^stripe-setup$', views.UserEntersBasicStripeAccountInformationAndAcceptsTerms.as_view(), name='connect'),
    url(r'^stripe-setup/cards$', views.UserCards.as_view(), name='cards'),
    url(r'^stripe-setup/banks$', views.UserBankAccounts.as_view(), name='banks'),
]