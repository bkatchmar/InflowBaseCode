from __future__ import unicode_literals
# InFlow Libraries
from accounts.models import UserSettings
from talktostripe.stripecommunication import StripeCommunication
# Django Libraries
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
# External Libraries
from dateutil.parser import parse
import requests
import stripe
import time
import urllib.parse

class BaseTalk(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'
    
    def get(self, request):
        context = {}
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user
            
        usersettings = usersettings.get_settings_based_on_user(currentlyloggedinuser)
        
        # Call Stripe Settings For The Link Generation
        context["call_state"] = settings.STRIPE_CALL_STATE
        context["stripe_acct"] = settings.STRIPE_ACCOUNT_ID
        
        # If this is from a Stripe Auth Page
        comm = StripeCommunication()
        response_code = request.GET.get("code", "")
        json_response = {}
        
        if response_code != "":
            json_response = comm.create_new_stripe_custom_account(response_code)
            
        if "stripe_user_id" in json_response:
            print("Found Stripe User ID")
            print(json_response["stripe_user_id"])
            
        if "error_description" in json_response:
            context["error_description"] = json_response["error_description"]
        
        return render(request, self.template_name, context)
    
class BaseExpressTalk(LoginRequiredMixin, TemplateView):
    template_name = "base-express.html"
    
    def get(self, request):
        context = {
            "redirect_uri" : urllib.parse.quote(settings.STRIPE_REDIRECT_URI),
            "client_id" : settings.STRIPE_ACCOUNT_ID,
            "state" : settings.STRIPE_CALL_STATE
        }
        
        # If this is from a Stripe Auth Page
        comm = StripeCommunication()
        response_code = request.GET.get("code", "")
        json_response = {}
        
        if response_code != "":
            json_response = comm.create_new_stripe_custom_account(response_code)
            
        if "stripe_user_id" in json_response:
            print("Found Stripe User ID")
            print(json_response["stripe_user_id"])
            
        if "error_description" in json_response:
            context["error_description"] = json_response["error_description"]
        
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
                context["ssnLastFourProvided"] = stripeAccount.legal_entity.ssn_last_4_provided
                context["personalIdProvided"] = stripeAccount.legal_entity.personal_id_number_provided
                
                if (stripeAccount.legal_entity.type == "company"):
                   context["businessTaxId"] = stripeAccount.legal_entity.business_tax_id_provided
            if (stripeAccount.legal_entity.address):
                context["legalEntityAddress"] = stripeAccount.legal_entity.address
            if (stripeAccount.legal_entity.dob and stripeAccount.legal_entity.dob.month):
                context["legalEntityDob"] = stripeAccount.legal_entity.dob
                context["legalEntityDob"]["zeroBasedIndexMonth"] = stripeAccount.legal_entity.dob.month-1
            if (stripeAccount.legal_entity.business_name):
                context["legalEntityBusinessName"] = stripeAccount.legal_entity.business_name
        except stripe.error.PermissionError as e:
            return redirect('stripebasepoint')
        except Exception as e:
            return redirect('stripebasepoint')
        
        return render(request, self.template_name, context)
        
    def post(self, request):
        userSettings = self.getUserSettings(request)
        context = {}
        context["settings"] = userSettings
        
        try:
            # Check if this account even exists in stripe
            stripe.api_key = settings.STRIPE_TEST_API_SECRET
            stripeAccount = stripe.Account.retrieve(userSettings.StripeConnectAccountKey)
            
            if (stripeAccount.legal_entity.type):
                context["legalEntityType"] = stripeAccount.legal_entity.type
                context["ssnLastFourProvided"] = stripeAccount.legal_entity.ssn_last_4_provided
                context["personalIdProvided"] = stripeAccount.legal_entity.personal_id_number_provided
                
                if (stripeAccount.legal_entity.type == "company"):
                   context["businessTaxId"] = stripeAccount.legal_entity.business_tax_id_provided
            if (stripeAccount.legal_entity.address):
                context["legalEntityAddress"] = stripeAccount.legal_entity.address
            if (stripeAccount.legal_entity.dob and stripeAccount.legal_entity.dob.month):
                context["legalEntityDob"] = stripeAccount.legal_entity.dob
                context["legalEntityDob"]["zeroBasedIndexMonth"] = stripeAccount.legal_entity.dob.month-1
            if (stripeAccount.legal_entity.business_name):
                context["legalEntityBusinessName"] = stripeAccount.legal_entity.business_name
        except stripe.error.PermissionError as e:
            return redirect('stripebasepoint')
        except Exception as e:
            return redirect('stripebasepoint')
        
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

        usersettings = usersettings.get_settings_based_on_user(currentlyloggedinuser)
        return usersettings
    
class UserCards(LoginRequiredMixin, TemplateView):
    template_name = "card.html"
    
    def get(self, request):
        userSettings = self.getUserSettings(request)
        context = {}
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        # Get the customer object and add the new card
        stripeApiCustomerObject = stripe.Customer.retrieve(userSettings.StripeApiCustomerKey)
        customerCards = stripeApiCustomerObject.sources.all(object="card")
        
        context["currentcards"] = customerCards
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        userSettings = self.getUserSettings(request)
        context = {}
        createdToken = request.POST.get("stripeToken","")
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        # Get the customer object and add the new card
        stripeApiCustomerObject = stripe.Customer.retrieve(userSettings.StripeApiCustomerKey)
        stripeApiCustomerObject.sources.create(source=createdToken)
        
        customerCards = stripeApiCustomerObject.sources.all(object="card")
        context["currentcards"] = customerCards
        
        return render(request, self.template_name, context)
    
    def getUserSettings(self, request):
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user

        usersettings = usersettings.get_settings_based_on_user(currentlyloggedinuser)
        return usersettings
    
class UserBankAccounts(LoginRequiredMixin, TemplateView):
    template_name = "bank.html"
    
    def get(self, request):
        context = {}
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        userSettings = self.getUserSettings(request)
        stripeAccount = stripe.Account.retrieve(userSettings.StripeConnectAccountKey)
        
        context["BaseCountry"] = userSettings.BaseCountry
        context["HolderName"] = ("%s %s" % (userSettings.UserAccount.first_name,userSettings.UserAccount.last_name))
        context["BankAccounts"] = stripeAccount.external_accounts
        
        if (stripeAccount.legal_entity.type):
            context["legalEntityType"] = stripeAccount.legal_entity.type
        else:
            context["legalEntityType"] = "individual"
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        userSettings = self.getUserSettings(request)
        stripeAccount = stripe.Account.retrieve(userSettings.StripeConnectAccountKey)
        
        context["BaseCountry"] = userSettings.BaseCountry
        context["HolderName"] = ("%s %s" % (userSettings.UserAccount.first_name,userSettings.UserAccount.last_name))
        context["BankAccounts"] = stripeAccount.external_accounts
        
        if (stripeAccount.legal_entity.type):
            context["legalEntityType"] = stripeAccount.legal_entity.type
        else:
            context["legalEntityType"] = "individual"
            
        createdToken = request.POST.get("stripeToken", "")
        context["inputToken"] = request.POST.get("stripeToken", "")
        
        if (createdToken is not None):
            stripeAccount.external_accounts.create(external_account=createdToken)
            
        # stripe.Account.retrieve({ACCOUNT_ID}).external_accounts.all(object="bank_account")
        
        return render(request, self.template_name, context)
    
    def getUserSettings(self, request):
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user
            
        usersettings = usersettings.get_settings_based_on_user(currentlyloggedinuser)
        return usersettings