from __future__ import unicode_literals
from accounts.linkedincalls import LinkedInApi
from accounts.models import UserSettings
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from inflowco.models import Currency
import requests

class LoginView(TemplateView):
    template_name = "login.html"
    
    def get(self, request):
        context = {'message':''}
        if request.GET.get("logout","") != "":
            logout(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {'message':''}
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/inflow/currencies/')
        
        return render(request, self.template_name, context)
    
class LinkedInHandler(TemplateView):
    template_name = 'linkedin.html'
    
    def get(self, request):
        context = {'message':''}
        
        # Getting info from the request
        linkedinerror = request.GET.get('error', '')
        linkedinerorrmsg = request.GET.get('error_description', '')
        responsestate = request.GET.get('state', '')
        authtokencode = request.GET.get('code', '')
        
        # Validation Checks
        returnstatematches = False
        propercodehasbeenreturned = False
        collectedaccesstoken = ""
        
        if linkedinerror is not None:
            context["linkedinerorrmsg"] = linkedinerorrmsg
            
        if responsestate != "":
            if responsestate != settings.LINKEDIN_CALL_STATE:
                context["linkedinerorrmsg"] = "State does not match, something fishy is going on"
            else:
                returnstatematches = True
                
        if authtokencode is not None:
            propercodehasbeenreturned = True
            
        # If everything checks out, time to ROCK AND ROLL
        if returnstatematches and propercodehasbeenreturned:
            apiCaller = LinkedInApi()
            json = apiCaller.RequestAuthorizationToken(authtokencode)
            
            if json.get("access_token") is not None:
                context["message"] = "You Have Successfully Authorized"
                collectedaccesstoken = json.get("access_token")
            if json.get("error_description") is not None:
                context["linkedinerorrmsg"] = json["error_description"]
                
            context["linkedinresponsebody"] = json
            
        # Next, we handle account create an authorization, if a user is already logged in, this LinkedIn info will be tied to that account
        # Otherwise, we are going to create a brand new user based on what we read from LinkedIn
        if collectedaccesstoken != "":
            if request.user.is_authenticated:
                usersettings = UserSettings()
                usersettings = usersettings.GetSettingsBasedOnUser(request.user)
                usersettings.LinkedInAccessToken = collectedaccesstoken
                usersettings.save()
            else:
                apicaller = LinkedInApi()
                apilinkedininfo = apicaller.GetBasicProfileInfo(collectedaccesstoken)
                newlycreateduser = User.objects.create(username=apilinkedininfo["emailAddress"],email=apilinkedininfo["emailAddress"],first_name=apilinkedininfo["firstName"],last_name=apilinkedininfo["lastName"],is_staff=False,is_active=True,is_superuser=False)
                newlycreateduser.set_password("linkedinprofilenopasswordneeded")
                newlycreateduser.save()
                
                usersettings = UserSettings()
                usersettings = usersettings.GetSettingsBasedOnUser(newlycreateduser)
                usersettings.LinkedInAccessToken = collectedaccesstoken
                usersettings.save()
                
                user = authenticate(request, username=apilinkedininfo["emailAddress"], password="linkedinprofilenopasswordneeded")
                if user is not None:
                    login(request, user)
                    return redirect("/inflow/account/")
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {'message':''}
        return render(request, self.template_name, context)
    
class CurrencyListView(LoginRequiredMixin, TemplateView):
    template_name = 'listcurrencies.html'
    
    def get_queryset(self):
        return Currency.objects.all()
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CurrencyListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the currencies
        context['currencies'] = self.get_queryset()
        return context