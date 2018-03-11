from __future__ import unicode_literals
# From Accounts App
from accounts.externalapicalls import LinkedInApi
from accounts.inflowaccountloginview import InflowLoginView
from accounts.models import UserLinkedInInformation, UserSettings, UserType, UserAssociatedTypes
from accounts.models import FREELANCER_ANSWER_FREQUENCY, FREELANCER_WORK_WITH, FREELANCER_INTERESTED_IN
from accounts.signupvalidation import UserCreationBaseValidators
# Django references
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse
# Base InFlow Models
from inflowco.models import Country, Currency

class AccountLoginView(TemplateView,InflowLoginView):
    template_name = "account.login.html"
    
    def get(self, request):
        logout(request)
        context = { "linkedin" : self.set_linkedin_params(), "show_nav" : True }
        
        # If this page was hit from LinkedIn, go ahead and handle to log the user in
        if self.is_this_a_linkedin_request(request):
            return self.handle_linkedin_request(request)
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = { "linkedin" : self.set_linkedin_params(), "show_nav" : True }
        
        # Collect POST data
        user_name = request.POST.get("username", "")
        password = request.POST.get("password", "")
        google_id_token = request.POST.get("google-id-token", "")
        
        if google_id_token != "":
            return self.handle_google_login_attempt(request,google_id_token)
        
        # If we get here, means Google and LinkedIn do not apply to this post
        user = authenticate(request, username=user_name, password=password)
        
        if user is not None:
            login(request, user)
            
            if self.determine_if_user_needs_onboarding(user):
                return redirect(reverse("accounts:onboarding_1"))
            else:
                return redirect(reverse("base:dashboard"))
        else:
            context["error_msg"] = "Username and Password Combination Are Not Correct"
        
        context["linkedin"] = self.set_linkedin_params()
        return render(request, self.template_name, context)

class CreateAccountView(TemplateView, InflowLoginView):
    template_name = "create.account.html"
    
    def get(self, request):
        logout(request)
        context = { "linkedin" : self.set_linkedin_params(), "show_nav" : True }
        
        # If this page was hit from LinkedIn, go ahead and handle to log the user in
        if self.is_this_a_linkedin_request(request):
            return self.handle_linkedin_request(request)
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = { "linkedin" : self.set_linkedin_params(), "show_nav" : True }
        
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
            return redirect(reverse("accounts:onboarding_1"))
        
        return render(request, self.template_name, context)

class OnboardingStepOneView(LoginRequiredMixin,TemplateView):
    template_name = "onboarding.step1.html"
    all_user_types = UserType.objects.all()
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = self.get_context_data(request)
        
        selected_frequency = request.POST.get("frequency", UserSettings._meta.get_field("FreelancerFrequency").get_default())
        
        # Go through each UserType and see what was selected, add that to the DB
        # Remove anything that was previously selected
        UserAssociatedTypes.objects.filter(UserAccount=request.user).delete()
        for type in self.all_user_types:
            current_type = request.POST.get(type.Name, "")
            
            if current_type == "on":
                UserAssociatedTypes.objects.create(UserAccount=request.user,UserFreelanceType=type)
            
        # Build up user settings or fetch previously saved ones, then save what was selected as the freelancer frequency type
        usersettings = UserSettings()
        usersettings = usersettings.get_settings_based_on_user(request.user)
        usersettings.FreelancerFrequency = selected_frequency
        usersettings.save()
        
        return redirect(reverse("accounts:onboarding_2"))
    
    def get_context_data(self, request, **kwargs):
        context = {}
        
        # Go through each UserType and see what was selected, add a dictionary set to True for each
        user_types = self.all_user_types
        associated_types = UserAssociatedTypes.objects.filter(UserAccount=request.user)
        
        for type in user_types:
            for associated_type in associated_types:
                if type.id == associated_type.UserFreelanceType.id:
                    type.Selected = True
        
        # Set context for view
        context["name"] = request.user.first_name
        context["user_types"] = user_types
        context["frequencies"] = FREELANCER_ANSWER_FREQUENCY

        return context
    
class OnboardingStepTwoView(LoginRequiredMixin,TemplateView):
    template_name = "onboarding.step2.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = self.get_context_data(request)
        
        # Gather Data From Post
        selected_work_with = request.POST.get("work-with", UserSettings._meta.get_field("FreelancerWorkWith").get_default())
        selected_feature = request.POST.get("feature", UserSettings._meta.get_field("FreelancerInterestedIn").get_default())
        
        # Build up user settings or fetch previously saved ones, then save what was selected as the freelancer work with and interested in
        usersettings = UserSettings()
        usersettings = usersettings.get_settings_based_on_user(request.user)
        usersettings.FreelancerWorkWith = selected_work_with
        usersettings.FreelancerInterestedIn = selected_feature
        usersettings.save()
        
        return redirect(reverse("accounts:onboarding_3"))
    
    def get_context_data(self, request, **kwargs):
        context = {}
        
        # Set context for view
        context["name"] = request.user.first_name
        context["work_with"] = FREELANCER_WORK_WITH
        context["interested_in"] = FREELANCER_INTERESTED_IN

        return context

class OnboardingStepThreeView(LoginRequiredMixin,TemplateView):
    template_name = "onboarding.step3.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = self.get_context_data(request)
        
        # Gather Data From Post
        business_name = request.POST.get("business-name", "")
        region = request.POST.get("region", "")
        
        # Build up user settings or fetch previously saved ones, then save what was selected as the freelancer work with and interested in
        usersettings = UserSettings()
        usersettings = usersettings.get_settings_based_on_user(request.user)
        usersettings.BusinessName = business_name
        usersettings.Region = region
        usersettings.save()
        
        return redirect(reverse("base:dashboard"))
    
    def get_context_data(self, request, **kwargs):
        context = {}
        
        # Get user content settings
        usersettings = UserSettings()
        usersettings = usersettings.get_settings_based_on_user(request.user)
        
        # Set context for view
        context["name"] = request.user.first_name
        context["country"] = Country.objects.all()
        context["currency"] = Currency.objects.all()
        context["selected_country"] = usersettings.BaseCountry.IdCountry
        context["selected_country_currency"] = usersettings.BaseCountry.PrimaryCurrency.IdCurrency

        return context