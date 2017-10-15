from __future__ import unicode_literals
from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from accounts.models import UserSettings
from talktostripe.stripecommunication import StripeCommunication
import requests
import stripe
import time

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
        comm.CreateNewStripeCustomAccount(usersettings)
        
        return render(request, self.template_name, context)
    
class UserEntersBasicStripeAccountInformationAndAcceptsTerms(LoginRequiredMixin, TemplateView):
    template_name = "verifystripeinfo.html"
    
    def get(self, request):
        userSettings = self.getUserSettings(request)
        context = {}
        context["settings"] = userSettings
        
        try:
            # Check if this account even exists in stripe
            stripe.api_key = settings.STRIPE_TEST_API_SECRET
            stripeAccount = stripe.Account.retrieve(userSettings.StripeConnectAccountKey)
            
            if (stripeAccount.legal_entity.type):
                context["legalEntityType"] = stripeAccount.legal_entity.type
            if (stripeAccount.legal_entity.address):
                context["legalEntityAddress"] = stripeAccount.legal_entity.address
            if (stripeAccount.legal_entity.dob and stripeAccount.legal_entity.dob.month):
                context["legalEntityDob"] = stripeAccount.legal_entity.dob
                context["legalEntityDob"]["zeroBasedIndexMonth"] = stripeAccount.legal_entity.dob.month-1
        except stripe.error.PermissionError as e:
            return redirect('stripebasepoint')
        except Exception as e:
            return redirect('stripebasepoint')
        
        return render(request, self.template_name, context)
        
    def post(self, request):
        userSettings = self.getUserSettings(request)
        context = {}
        parsedDateTime = parse(request.POST.get("date-of-birth", ""))
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        stripeAccount = stripe.Account.retrieve(userSettings.StripeConnectAccountKey)
        
        if (stripeAccount):
            stripeAccount.legal_entity.dob.day = parsedDateTime.day
            stripeAccount.legal_entity.dob.month = parsedDateTime.month
            stripeAccount.legal_entity.dob.year = parsedDateTime.year
            stripeAccount.legal_entity.type = request.POST.get("legal-entity-type", "")
            stripeAccount.legal_entity.address.line1 = request.POST.get("address-1", "")
            stripeAccount.legal_entity.address.city = request.POST.get("address-city", "")
            stripeAccount.legal_entity.address.state = request.POST.get("address-state", "")
            stripeAccount.legal_entity.address.postal_code = request.POST.get("address-zip", "")
            
            if not (stripeAccount.tos_acceptance.date):
                stripeAccount.tos_acceptance.date = int(time.time())
                stripeAccount.tos_acceptance.ip = self.getClientIP(request)
                
            stripeAccount.save()
        
        context["settings"] = userSettings
        context["successMessage"] = "Account Successfully Verified"
        context["legalEntityType"] = stripeAccount.legal_entity.type
        context["legalEntityDob"] = stripeAccount.legal_entity.dob
        context["legalEntityDob"]["zeroBasedIndexMonth"] = stripeAccount.legal_entity.dob.month-1
        context["legalEntityAddress"] = stripeAccount.legal_entity.address
        
        return render(request, self.template_name, context)
    
    def getClientIP(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if (x_forwarded_for):
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip
    
    def getUserSettings(self, request):
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user

        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        return usersettings
    
class ConnectStripeToAccount(LoginRequiredMixin, TemplateView):
    def get(self, request):
        context = {
                   "stripeClientId" : settings.STRIPE_CONNECT_ACCOUNT
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
        
        if (stripe_code):
            dataToStripe = {
                            "grant_type": "authorization_code",
                            "client_id": settings.STRIPE_CONNECT_ACCOUNT,
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