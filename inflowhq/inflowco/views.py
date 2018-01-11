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
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import urlquote
from django.views.generic import TemplateView
# Entire Libraries where we are not extracting specific things
import boto3
import botocore
import urllib.parse

class LoginView(TemplateView):
    template_name = "login.html"
    
    def get(self, request):
        # Log out current user if the query string has "logout" on it
        if request.GET.get("logout","") != "":
            logout(request)
            
        return render(request, self.template_name)
    
    def post(self, request):
        # Collect POST data
        user_name = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=user_name, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("/inflow/currencies/")
        
        return render(request, self.template_name)
    
class LinkedInHandler(TemplateView):
    template_name = 'linkedin.html'
    
    def get(self, request):
        context = {}
        
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
        apicaller = LinkedInApi()
        apilinkedininfo = apicaller.GetBasicProfileInfo(collectedaccesstoken)
        
        if collectedaccesstoken != "":
            if request.user.is_authenticated:
                userLinkedInProfileInfo = UserLinkedInInformation.objects.filter(UserAccount=request.user).first()
                if userLinkedInProfileInfo is None:
                    UserLinkedInInformation.objects.create(UserAccount=request.user,LinkedInProfileID=apilinkedininfo["id"],LinkedInAccessToken=collectedaccesstoken)
                else:
                    userLinkedInProfileInfo.LinkedInProfileID = apilinkedininfo["id"]
                    userLinkedInProfileInfo.LinkedInAccessToken = collectedaccesstoken
                    userLinkedInProfileInfo.save()
            else:
                linkedin_profile_information = UserLinkedInInformation.objects.filter(LinkedInProfileID=apilinkedininfo["id"]).first()
                
                if linkedin_profile_information is None:
                    newlycreateduser = User.objects.create(username=apilinkedininfo["emailAddress"],email=apilinkedininfo["emailAddress"],first_name=apilinkedininfo["firstName"],last_name=apilinkedininfo["lastName"],is_staff=False,is_active=True,is_superuser=False)
                    newlycreateduser.set_password("linkedinprofilenopasswordneeded")
                    newlycreateduser.save()
                    UserLinkedInInformation.objects.create(UserAccount=newlycreateduser,LinkedInProfileID=apilinkedininfo["id"],LinkedInAccessToken=collectedaccesstoken)
                
                user = authenticate(request, username=apilinkedininfo["emailAddress"], password="linkedinprofilenopasswordneeded")
                if user is not None:
                    login(request, user)
                    return redirect("/inflow/account/")
        
        return render(request, self.template_name, context)

class GoogleHandler(TemplateView):
    template_name = "googlelogin.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        # Collect Post Information
        google_id_token = request.POST.get("google-id-token", "")
        
        # First we need to send google_id_token for validation, make sure this request is legit
        google_api_caller = GoogleApi()
        google_api_response = google_api_caller.validate_google_token(google_id_token)
        
        # If something went wrong, it means something is fishy, perhaps a third party attack, abort and go back to the login screen
        if google_api_response["response_ok"] == False:
            return render(request, self.template_name)
        if google_api_response["email"] is None:
            return render(request, self.template_name)
        if google_api_response["sub"] is None:
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
                return redirect("/inflow/account/")
            else:
                # Link Google To Existing User
                UserGoogleInformation.objects.create(UserAccount=user,
                                                     GoogleProfileID=google_api_response["sub"],
                                                     GoogleProfileName=google_api_response["name"],
                                                     GoogleImageUrl=google_api_response["picture"])
                login(request, newly_created_user)
                return redirect("/inflow/account/")
        else:
            # User exists, go ahead and log them in
            login(request, user_google_information.UserAccount)
            return redirect("/inflow/account/")
        
        return render(request, self.template_name)
    
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
    
class SendEmail(LoginRequiredMixin, TemplateView):
    template_name = "sendemail.html"
    
    def get(self, request):
        # Set the Context
        context = {}
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Set the Context
        context = {}
        send_mail("Statement of Truth",
            "I Like Chicken Fingers, Pizza, Bacon, Cereal, and Ice Cream",
            "brian@workinflow.co",
            ["bkatchmar@gmail.com"],
            fail_silently=False)
        return render(request, self.template_name, context)

class SavePdfTrials(PDFTemplateView):
    template_name = "basepdftemplate.html"