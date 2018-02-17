from __future__ import unicode_literals # I have no idea what this even is
# References from our own library
from accounts.externalapicalls import GoogleApi, LinkedInApi
from accounts.models import UserGoogleInformation, UserLinkedInInformation, UserSettings
from inflowco.models import Currency
from easy_pdf.views import PDFTemplateView
# Django references
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
# Entire Libraries where we are not extracting specific things
import boto3
import botocore
import urllib.parse

class LoginView(TemplateView):
    template_name = "login.html"
    
    def get(self, request):
        context = {}
        
        # Log out current user if the query string has "logout" on it
        if request.GET.get("logout","") != "":
            context["try_process_login"] = False
            logout(request)
        else:
            context["try_process_login"] = True
        
        # For LinkedIn
        context["linkedin"] = self.set_linkedin_params()
        
        # If this page was hit from LinkedIn, go ahead and handle to log the user in
        if self.is_this_a_linkedin_request(request):
            return self.handle_linkedin_request(request)
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        
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
            return redirect("/inflow/currencies/")
        else:
            context["error_msg"] = "Username and Password Combination Are Not Correct"
        
        context["linkedin"] = self.set_linkedin_params()
        return render(request, self.template_name, context)
    
    def handle_google_login_attempt(self,request,google_id_token):
        # First we need to send google_id_token for validation, make sure this request is legit
        login_attempt_failed = False
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
                UserGoogleInformation.objects.create(UserAccount=newly_created_user,
                                                     GoogleProfileID=google_api_response["sub"],
                                                     GoogleProfileName=google_api_response["name"],
                                                     GoogleImageUrl=google_api_response["picture"])
                login(request, newly_created_user)
            else:
                # Link Google To Existing User
                UserGoogleInformation.objects.create(UserAccount=user,
                                                     GoogleProfileID=google_api_response["sub"],
                                                     GoogleProfileName=google_api_response["name"],
                                                     GoogleImageUrl=google_api_response["picture"])
                login(request, user)
        else:
            # User exists, go ahead and log them in
            login(request, user_google_information.UserAccount)
        
        return redirect("/inflow/currencies/")
    
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
            return redirect("/inflow/currencies/")
        
        context["linkedin"] = self.set_linkedin_params()
        return render(request, self.template_name, context)
    
class CurrencyListView(LoginRequiredMixin, TemplateView):
    template_name = 'listcurrencies.html'
    
    def get_queryset(self):
        return Currency.objects.all()
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CurrencyListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the currencies
        context["currencies"] = self.get_queryset()
        return context

class AmazonBotoExamples(LoginRequiredMixin, TemplateView):
    template_name = "boto3.html"
    
    def get(self, request):
        # Set the Context
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Set the Context
        context = self.get_context_data(request)
        
        # Get data from the POST
        uploaded_deliverable = request.FILES.get("deliverable", False)
        
        # If the user actually send something over, lets capture it and upload it to S3
        if uploaded_deliverable != False:
            deliverable_key = uploaded_deliverable.__str__()
            context["deliverable_bucket"].put_object(Key=deliverable_key, Body=uploaded_deliverable)
            context["file_names"].append({"key":deliverable_key,"qs":urllib.parse.quote_plus(deliverable_key)})
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Call the base implementation first to get a context
        context = super(AmazonBotoExamples, self).get_context_data(**kwargs)
        
        # Instantiate items related to the context
        file_names = []
        amazon_caller = boto3.resource("s3")
        deliverable_bucket_name = self.generate_bucket_name(request.user)
        amazon_caller.create_bucket(Bucket=deliverable_bucket_name)
        deliverable_bucket = amazon_caller.Bucket(deliverable_bucket_name)
        
        # Fill in the bucket key names
        for object in deliverable_bucket.objects.all():
            file_names.append({"key":object.key,"qs":urllib.parse.quote_plus(object.key)})
            object.Acl().put(ACL="public-read")
        
        context["file_names"] = file_names
        context["deliverable_bucket"] = deliverable_bucket
        
        return context
    
    def generate_bucket_name(self,user):
        return ("inflow-user-bucket-%s" % (user.id))
    
class SavePdfTrials(PDFTemplateView):
    template_name = "basepdftemplate.html"
    
class BaseSitemap(Sitemap):
    def items(self):
        return ["login",
                "htmldemos:demo_home",
                "htmldemos:demo_my_projects",
                "htmldemos:demo_project_details",
                "htmldemos:demo_create_contract",
                "htmldemos:demo_amend_contract",
                "htmldemos:demo_upload_milestone",
                "htmldemos:demo_preview_milestone",
                "htmldemos:demo_create_contract_freelancer",
                "htmldemos:demo_create_contract_client",
                "htmldemos:demo_create_contract_received_email",
                "htmldemos:demo_create_contract_client_email_signed",
                "htmldemos:demo_create_contract_client_email_revision",
                "htmldemos:demo_create_contract_freelance_email_signed",
                "htmldemos:demo_create_contract_freelance_email_revision",
                "htmldemos:demo_welcome",
                "htmldemos:demo_address",
                "htmldemos:demo_congratulation",
                "htmldemos:demo_stripe_connect",
                "htmldemos:demo_stripe_thanks",
                "htmldemos:demo_tos",
                "htmldemos:demo_upload_milestone_drag"]

    def location(self, item):
        return reverse(item)
    
    def changefreq(self, item):
        if item == "htmldemos:demo_home":
            return "daily"
        elif item == "htmldemos:demo_my_projects":
            return "yearly"
        else: 
            return "never"
        
    def priority(self, item):
        return 0.5
    
class GoogleDomainVerificationFile(TemplateView):
    template_name = "google255e09f84b6b193b.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)