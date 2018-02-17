from __future__ import unicode_literals
# From Accounts App
from accounts.externalapicalls import LinkedInApi
from accounts.inflowaccountloginview import InflowLoginView
from accounts.models import UserLinkedInInformation, UserSettings
from accounts.signupvalidation import UserCreationBaseValidators
# Django references
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

class CreateAccountView(TemplateView, InflowLoginView):
    template_name = "create.account.html"
    
    def get(self, request):
        logout(request)
        context = { "linkedin" : self.set_linkedin_params() }
        
        # If this page was hit from LinkedIn, go ahead and handle to log the user in
        if self.is_this_a_linkedin_request(request):
            return self.handle_linkedin_request(request)
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = { "linkedin" : self.set_linkedin_params() }
        
        google_id_token = request.POST.get("google-id-token", "")
        
        if google_id_token != "":
            return self.handle_google_login_attempt(request,google_id_token)
        
        # Handle this as a standard sign up request
        # Gather user form data
        username = request.POST.get("username", "")
        name = request.POST.get("name", "")
        password = request.POST.get("password", "")
        agreed = request.POST.get("agree", False)
        
        # Time to validate the entries
        validator = UserCreationBaseValidators()
        validator.attempt_to_create_user(username,name,password,agreed)
        
        if validator.error_thrown:
            context["error_msg"] = validator.error_message
        else:
            login(request, validator.created_user)
            return redirect("/inflow/currencies/")
        
        return render(request, self.template_name, context)

class AccountInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'viewaccountinfo.html'
    
    def get(self, request):
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user

        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        context = {
                   'settings':usersettings
                   }
        
        userLinkedInProfileInfo = UserLinkedInInformation.objects.filter(UserAccount=currentlyloggedinuser).first()
        if userLinkedInProfileInfo is not None:
            if userLinkedInProfileInfo.LinkedInAccessToken != "":
                apiCaller = LinkedInApi()
                apiLinkeIinInfo = apiCaller.GetBasicProfileInfo(userLinkedInProfileInfo.LinkedInAccessToken)
                context["linkedininfo"] = apiLinkeIinInfo
        
        return render(request, self.template_name, context)