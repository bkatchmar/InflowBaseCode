from __future__ import unicode_literals
from accounts.linkedincalls import LinkedInApi
from accounts.models import UserLinkedInInformation, UserSettings
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.http import urlquote
from django.views.generic import TemplateView
from inflowco.models import Currency
import boto3

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
                newlycreateduser = User.objects.create(username=apilinkedininfo["emailAddress"],email=apilinkedininfo["emailAddress"],first_name=apilinkedininfo["firstName"],last_name=apilinkedininfo["lastName"],is_staff=False,is_active=True,is_superuser=False)
                newlycreateduser.set_password("linkedinprofilenopasswordneeded")
                newlycreateduser.save()
                
                UserLinkedInInformation.objects.create(UserAccount=newlycreateduser,LinkedInProfileID=apilinkedininfo["id"],LinkedInAccessToken=collectedaccesstoken)
                
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

class AmazonBotoExamples(LoginRequiredMixin, TemplateView):
    template_name = "boto3.html"
    
    def get(self, request):
        context = {"message":""}
        amazonCaller = boto3.resource("s3")
        bucketNames = []
        deliverableBucket = amazonCaller.Bucket("inflow-deliverables-2")
        
        for object in deliverableBucket.objects.all():
            bucketNames.append(object.key)
            
        context["bucketNames"] = bucketNames
        context["folderName"] = request.user.username
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        amazonCaller = boto3.resource("s3")
        deliverableBucket = amazonCaller.Bucket("inflow-deliverables-2")
        uploadedDeliverable = request.FILES.get("deliverable", False)
        
        if uploadedDeliverable != False:
            deliverableBucket.put_object(Key=("%s/%s" % (request.user.username, uploadedDeliverable.__str__())), Body=uploadedDeliverable)
        
        return render(request, self.template_name, context)