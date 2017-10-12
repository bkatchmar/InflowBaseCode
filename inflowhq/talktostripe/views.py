from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from accounts.models import UserSettings
from talktostripe.stripecommunication import StripeCommunication
import requests
import stripe

class BaseTalk(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'
    
    def get(self, request):
        context = {}
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user
            
        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        
        comm = StripeCommunication()
        comm.CreateNewStripeCustomerWithId(usersettings)
        
        return render(request, 'base.html', context)
    
class ConnectStripeToAccount(LoginRequiredMixin, TemplateView):
    def get(self, request):
        context = {
                   "stripeClientId" : "ca_BZ2S2qzm663IIsbO9ObrkG3k6sbXAyIV"
                   }
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user
            
        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        
        return render(request, 'setupstripe.html', context)
    
class StripeConnectResult(LoginRequiredMixin, TemplateView):
    def get(self, request):
        context = {
                   "resultMsg" : "You Haven't Tried Anything Yet"
                   }
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user
            
        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        
        # Start collecting Query String Info
        stripe_code = request.GET["code"]
        
        if(stripe_code):
            dataToStripe = {
                            "grant_type": "authorization_code",
                            "client_id": "ca_BZ2S2qzm663IIsbO9ObrkG3k6sbXAyIV",
                            "client_secret": settings.STRIPE_TEST_API_SECRET,
                            "code": stripe_code
                            }
            strupeUrl = "https://connect.stripe.com/oauth/token"
            stripeResp = requests.post(strupeUrl, params=dataToStripe)
            
            token = stripeResp.json().get('stripe_user_id')
            context["resultMsg"] = "You have completed setup"
            usersettings.StripeConnectAccountKey = token
            usersettings.save()
        else:
            context["resultMsg"] = "You have canceled setup"
        
        return render(request, 'stripeconfirmation.html', context)