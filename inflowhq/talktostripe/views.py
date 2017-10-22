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
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        stripeAccount = stripe.Account.retrieve(userSettings.StripeConnectAccountKey)
        
        if (stripeAccount and request.POST.get("piiBusinessTaxNumber", "")):
            stripeAccount.legal_entity.business_tax_id = request.POST.get("piiBusinessTaxNumber", "")
            stripeAccount.save()
        elif (stripeAccount and request.POST.get("piiStripeToken", "")):
            stripeAccount.legal_entity.personal_id_number = request.POST.get("piiStripeToken", "")
            stripeAccount.save()
        elif (stripeAccount):
            parsedDateTime = parse(request.POST.get("date-of-birth", ""))
            stripeAccount.legal_entity.dob.day = parsedDateTime.day
            stripeAccount.legal_entity.dob.month = parsedDateTime.month
            stripeAccount.legal_entity.dob.year = parsedDateTime.year
            stripeAccount.legal_entity.type = request.POST.get("legal-entity-type", "")
            stripeAccount.legal_entity.address.line1 = request.POST.get("address-1", "")
            stripeAccount.legal_entity.address.city = request.POST.get("address-city", "")
            stripeAccount.legal_entity.address.state = request.POST.get("address-state", "")
            stripeAccount.legal_entity.address.postal_code = request.POST.get("address-zip", "")
            
            if request.POST.get("ssn-last-4", ""):
                stripeAccount.legal_entity.ssn_last_4 = request.POST.get("ssn-last-4", "")
                
            if request.POST.get("legal-entity-type", "") == "company":
                stripeAccount.legal_entity.business_name = request.POST.get("business-name", "")
                context["legalEntityBusinessName"] = stripeAccount.legal_entity.business_name
            
            if not (stripeAccount.tos_acceptance.date):
                stripeAccount.tos_acceptance.date = int(time.time())
                stripeAccount.tos_acceptance.ip = self.getClientIP(request)
                
            stripeAccount.save()
        
        context["settings"] = userSettings
        context["successMessage"] = "Account Successfully Verified"
        context["legalEntityType"] = stripeAccount.legal_entity.type
        context["ssnLastFourProvided"] = stripeAccount.legal_entity.ssn_last_4_provided
        context["personalIdProvided"] = stripeAccount.legal_entity.personal_id_number_provided
        context["legalEntityDob"] = stripeAccount.legal_entity.dob
        context["legalEntityDob"]["zeroBasedIndexMonth"] = stripeAccount.legal_entity.dob.month-1
        context["legalEntityAddress"] = stripeAccount.legal_entity.address
        
        if (stripeAccount.legal_entity.type == "company"):
            context["businessTaxId"] = stripeAccount.legal_entity.business_tax_id_provided
        
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

        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
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
            
        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        return usersettings