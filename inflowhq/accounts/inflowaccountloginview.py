# Account App References
from accounts.externalapicalls import GoogleApi, LinkedInApi
from accounts.models import UserGoogleInformation, UserLinkedInInformation, UserSettings, UserAssociatedTypes
# Django references
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
# Other Python Libraries
import urllib.parse

class InflowLoginView:
    def set_linkedin_params(self):
        linkedin_params = {
            "response_type" : "code",
            "client_id" : settings.LINKEDIN_CLIENT_ID,
            "state" : settings.LINKEDIN_CALL_STATE,
            "redirect_uri" : settings.LINKEDIN_REDIRECT_URL
        }
        return urllib.parse.urlencode(linkedin_params)
    
    def is_this_a_linkedin_request(self,request):
        responsestate = request.GET.get("state", "")
        return responsestate != ""
    
    def handle_linkedin_request(self,request):
        context = {}
        
        # Getting info from the request
        linkedin_error = request.GET.get("error", "")
        linkedin_error_msg = request.GET.get("error_description", "")
        response_state = request.GET.get("state", "")
        authtoken_code = request.GET.get("code", "")
        
        # Validation Checks
        return_state_matches = False
        proper_code_has_been_returned = False
        collected_access_token = ""
        
        if linkedin_error is not None:
            context["error_msg"] = linkedin_error_msg
            
        if response_state != "":
            if response_state != settings.LINKEDIN_CALL_STATE:
                context["error_msg"] = "LinkedIn State does not match"
            else:
                return_state_matches = True
                
        if authtoken_code is not None:
            proper_code_has_been_returned = True
            
        # If everything checks out, time to ROCK AND ROLL
        if return_state_matches and proper_code_has_been_returned:
            api_caller = LinkedInApi()
            json = api_caller.request_authorization_token(authtoken_code)
            
            if json.get("access_token") is not None:
                context["message"] = "You Have Successfully Authorized"
                collected_access_token = json.get("access_token")
            if json.get("error_description") is not None:
                context["error_msg"] = json["error_description"]
            
        # Next, we handle account create an authorization, if a user is already logged in, this LinkedIn info will be tied to that account
        # Otherwise, we are going to create a brand new user based on what we read from LinkedIn
        api_caller = LinkedInApi()
        api_linkedin_info = api_caller.get_basic_profile_info(collected_access_token)
        
        if collected_access_token != "":
            linkedin_profile_information = UserLinkedInInformation.objects.filter(LinkedInProfileID=api_linkedin_info["id"]).first()
            linkedin_user = User.objects.filter(email=api_linkedin_info["emailAddress"]).first()
            
            if linkedin_user is None:
                linkedin_user = User.objects.create(username=api_linkedin_info["emailAddress"],email=api_linkedin_info["emailAddress"],first_name=api_linkedin_info["firstName"],last_name=api_linkedin_info["lastName"],is_staff=False,is_active=True,is_superuser=False)
            
            if linkedin_profile_information is None:
                UserLinkedInInformation.objects.create(UserAccount=linkedin_user,LinkedInProfileID=api_linkedin_info["id"],LinkedInAccessToken=collected_access_token)
            else:
                linkedin_user = linkedin_profile_information.UserAccount
            
            login(request, linkedin_user)
            
            if self.determine_if_user_needs_onboarding(linkedin_user):
                return redirect(reverse("accounts:onboarding_1"))
            else:
                return redirect(reverse("base:dashboard"))
        
        context["linkedin"] = self.set_linkedin_params()
        return render(request, self.template_name, context)
    
    def handle_google_login_attempt(self,request,google_id_token):
        # First we need to send google_id_token for validation, make sure this request is legit
        login_attempt_failed = False
        context = { "error_msg" : "" }
        google_api_caller = GoogleApi()
        google_api_response = google_api_caller.validate_google_token(google_id_token)
        
        # If something went wrong, it means something is fishy, perhaps a third party attack, abort and go back to the login screen
        if google_api_response["response_ok"] == False:
            login_attempt_failed = True
        if google_api_response["email"] is None:
            login_attempt_failed = True
        if google_api_response["sub"] is None:
            login_attempt_failed = True
        
        # We don't need to continue if the login attempt faield
        if login_attempt_failed:
            logout(request)
            return render(request, self.template_name)
        
        # Call the Database to see if a user already exists for this Google User ID
        # TO DO: It may be appropriate to further identify the variables to see if they match what we got back from Google, but for now that may be overkill
        user_google_information = UserGoogleInformation.objects.filter(GoogleProfileID=google_api_response["sub"]).first()
        
        if user_google_information is None:
            # Nothing found, I want to check the email address to see if this user already registered, if they did, we can just log them in 
            user = User.objects.filter(email=google_api_response["email"]).first()
            
            if user is None:
                # Create A New User
                newly_created_user = User.objects.create(username=google_api_response["email"],
                                                        email=google_api_response["email"],
                                                        first_name=google_api_response["given_name"],
                                                        last_name=google_api_response["family_name"],
                                                        is_staff=False,
                                                        is_active=True,
                                                        is_superuser=False)
                user_google_information = UserGoogleInformation.objects.create(UserAccount=newly_created_user,
                                                     GoogleProfileID=google_api_response["sub"],
                                                     GoogleProfileName=google_api_response["name"],
                                                     GoogleImageUrl=google_api_response["picture"])
                login(request, newly_created_user)
            else:
                # Link Google To Existing User
                user_google_information = UserGoogleInformation.objects.create(UserAccount=user,
                                                     GoogleProfileID=google_api_response["sub"],
                                                     GoogleProfileName=google_api_response["name"],
                                                     GoogleImageUrl=google_api_response["picture"])
                login(request, user)
        else:
            # User exists, go ahead and log them in
            login(request, user_google_information.UserAccount)
        
        if self.determine_if_user_needs_onboarding(user_google_information.UserAccount):
            return redirect(reverse("accounts:onboarding_1"))
        else:
            return redirect(reverse("base:dashboard"))
    
    def determine_if_user_needs_onboarding(self,user):
        rtn_val = False # For now, assume the user has gone through this onboarding process already
        
        user_settings = UserSettings.objects.filter(UserAccount=user).first()
        user_selected_types = UserAssociatedTypes.objects.filter(UserAccount=user)
        
        if user_settings is None: # First is a basic check, does the user even have any settings?
            rtn_val = True
        elif len(user_selected_types) == 0: # User has not selected types
            rtn_val = True
        elif user_settings.BusinessName is None and user_settings.Region is None:
            rtn_val = True
        
        return rtn_val