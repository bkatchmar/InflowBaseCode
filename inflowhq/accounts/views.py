from __future__ import unicode_literals
# From Accounts App
from accounts.externalapicalls import LinkedInApi
from accounts.inflowaccountloginview import InflowLoginView
from accounts.models import NotificationSetting, UserNotificationSettings, UserSettings, UserType, UserAssociatedTypes, UserInterest, InFlowInvitation
from accounts.models import FREELANCER_ANSWER_FREQUENCY, FREELANCER_WORK_WITH, FREELANCER_INTERESTED_IN
from accounts.signupvalidation import UserCreationBaseValidators
# Inflow Stripe App
from talktostripe.stripecommunication import StripeCommunication
# Django references
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import Http404
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
    
class AccountInvitationView(TemplateView, InflowLoginView):
    template_name = "account.invitation.html"
    
    def get(self, request, **kwargs):
        logout(request)
        context = { "linkedin" : self.set_linkedin_params(), "show_nav" : True }
        
        # Get the invitation information
        guid = kwargs.get("invitation_guid")
        selected_invitation = InFlowInvitation.objects.filter(GUID=guid).first()
        
        if selected_invitation is None: # User entered a bogus GUID
            raise Http404()
        
        context["user_email"] = selected_invitation.InvitedUser.email
        
        # If this page was hit from LinkedIn, go ahead and handle to log the user in
        if self.is_this_a_linkedin_request(request):
            return self.handle_linkedin_request(request)
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
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
            return redirect(reverse("contracts:home"))
        
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
        other_text = request.POST.get("other", "")
        
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
        usersettings.OtherType = other_text
        usersettings.save()
        
        return redirect(reverse("accounts:onboarding_2"))
    
    def get_context_data(self, request, **kwargs):
        context = {}
        
        # Go through each UserType and see what was selected, add a dictionary set to True for each
        user_types = self.all_user_types
        associated_types = UserAssociatedTypes.objects.filter(UserAccount=request.user)
        
        for type in user_types:
            type.Selected = False # This seems to persist for some reason
            
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
        
        # Remove anything that was previously selected
        UserInterest.objects.filter(UserAccount=request.user).delete()
        
        for interest in FREELANCER_INTERESTED_IN:
            interest_point = request.POST.get(interest[0], "")
            
            if interest_point == "on":
                UserInterest.objects.create(UserAccount=request.user,Interest=interest[0])
        
        # Build up user settings or fetch previously saved ones, then save what was selected as the freelancer work with and interested in
        usersettings = UserSettings()
        usersettings = usersettings.get_settings_based_on_user(request.user)
        usersettings.FreelancerWorkWith = selected_work_with
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
        zip_code = request.POST.get("zip-code", "")
        
        # Build up user settings or fetch previously saved ones, then save what was selected as the freelancer work with and interested in
        usersettings = UserSettings()
        usersettings = usersettings.get_settings_based_on_user(request.user)
        usersettings.BusinessName = business_name
        usersettings.Region = region
        usersettings.ZipCode = zip_code
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
    
class EditProfileView(LoginRequiredMixin,TemplateView):
    template_name = "settings.edit.profile.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        
        # Get some necessary User Information
        older_email = request.user.email
        settings = UserSettings()
        settings = settings.get_settings_based_on_user(request.user)
        
        # Get values from the request
        first_name = request.POST.get("first-name", "")
        last_name = request.POST.get("last-name", "")
        email = request.POST.get("email-address", "")
        phone_number = request.POST.get("phone-number", "")
        
        # Update User
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.username = email
        settings.PhoneNumber = phone_number
        settings.save()
        
        # Update Context
        context["first_name"] = request.user.first_name
        context["last_name"] = request.user.last_name
        context["email"] = request.user.email
        context["phone_number"] = phone_number
        
        # Some basic exception handling, let the DB handle this part for us so users don't try to save duplicate names
        try:
            request.user.save()
        except IntegrityError:
            context["error_message"] = ("User with the email '%s' already exists" % email)
            context["email"] = older_email
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Get some necessary User Information
        settings = UserSettings()
        settings = settings.get_settings_based_on_user(request.user)
        
        context = super(EditProfileView, self).get_context_data(**kwargs)
        context["first_name"] = request.user.first_name
        context["last_name"] = request.user.last_name
        context["email"] = request.user.email
        
        if settings.PhoneNumber is None:
            context["phone_number"] = ""
        else:
            context["phone_number"] = settings.PhoneNumber
        
        return context

class EditAccountView(LoginRequiredMixin,TemplateView):
    template_name = "settings.edit.account.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        
        # If true, This call came from a Stripe page and came back with a User ID
        if context["came_from_stripe"] and context["user_stripe_acct"] != "":
            user_settings = UserSettings()
            user_settings = user_settings.get_settings_based_on_user(request.user)
            user_settings.StripeConnectAccountKey = context["user_stripe_acct"]
            user_settings.save()
            context["needs_stripe"] = False
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = self.get_context_data(request)
        
        # Get variables from request
        current_password = request.POST.get("current-password", "")
        new_password_1 = request.POST.get("new-password-1", "")
        new_password_2 = request.POST.get("new-password-2", "")
        
        # Check to see if the password entered is even correct
        if not request.user.check_password(current_password) and request.user.has_usable_password():
            context["error_message"] = "Current Password is not correct"
            return render(request, self.template_name, context)
        
        # Make the attempt to change the password
        if new_password_1 != "" and new_password_2 != "":
            if new_password_1 == new_password_2:
                validator = UserCreationBaseValidators()
                validator.try_to_validate_password(request.user,new_password_1,request)
                context["error_message"] = validator.error_message
            else:
                context["error_message"] = "Please Confirm Your New Password"
        
        if not validator.error_thrown:
            context["error_message"] = "Your password has been changed"

        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Get some necessary User Information
        user_settings = UserSettings()
        user_settings = user_settings.get_settings_based_on_user(request.user)
        
        # Set the context
        context = super(EditAccountView, self).get_context_data(**kwargs)
        
        # Call Stripe Settings For The Link Generation
        context["needs_stripe"] = user_settings.does_this_user_need_stripe()
        context["call_state"] = settings.STRIPE_CALL_STATE
        context["stripe_acct"] = settings.STRIPE_ACCOUNT_ID
        
        # If this is from a Stripe Auth Page
        comm = StripeCommunication()
        response_code = request.GET.get("code", "")
        stripe_state = request.GET.get("state", "")
        json_response = {}
        
        # We need to check if this request even came from Stripe
        if response_code != "":
            json_response = comm.create_new_stripe_custom_account(response_code)
            context["came_from_stripe"] = True
            
            if stripe_state != settings.STRIPE_CALL_STATE:
                context["error_message"] = "Bad Call State"
                context["needs_stripe"] = True
        else:
            context["came_from_stripe"] = False
        
        # Did we get the stripe User ID in the response?
        if "stripe_user_id" in json_response:
            context["user_stripe_acct"] = json_response["stripe_user_id"]
        else:
            context["user_stripe_acct"] = ""
        
        # Did the response come with an error description?
        if "error_description" in json_response:
            context["error_message"] = json_response["error_description"]
            context["needs_stripe"] = True
        
        return context
    
class EditNotificationsView(LoginRequiredMixin,TemplateView):
    template_name = "settings.edit.notifications.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        associated_settings = UserNotificationSettings.objects.filter(UserAccount=request.user)
        
        # Time to iterate through each setting, see what was clicked, and make the needed calls to the DB
        for type in self.all_settings:
            form_name = ("checkbox-%d" % type.id)
            form_value = request.POST.get(form_name, "")
            is_checked = (form_value == "on")
            
            # If we have an entry in the DB, we'll just update it, otherwise, create a new entry
            if associated_settings.filter(Setting=type).exists():
                UserNotificationSettings.objects.filter(Setting=type).update(Selected=is_checked)
            else:
                UserNotificationSettings.objects.create(UserAccount=request.user,Setting=type,Selected=is_checked)
        
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Build objects for context
        all_collected_info = []
        all_settings = NotificationSetting.objects.all()
        associated_settings = UserNotificationSettings.objects.filter(UserAccount=request.user)
        
        # Time to iterate through each setting, find the associated setting to the user (if any exists) and 
        for type in all_settings:
            setting_data = { "id" : type.id, "text" : type.SettingName, "selected" : False }
            
            for associated_setting in associated_settings:
                if type.id == associated_setting.Setting.id:
                    setting_data["selected"] = associated_setting.Selected
                
            all_collected_info.append(setting_data)
        
        # Set the context
        context = super(EditNotificationsView, self).get_context_data(**kwargs)
        context["settings"] = all_collected_info
        return context