from __future__ import unicode_literals # I have no idea what this even is
# References from our own library
from accounts.inflowaccountloginview import InflowLoginView
from inflowco.models import Currency
from easy_pdf.views import PDFTemplateView
# Django references
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
# Other Python Libraries
import boto3
import botocore
import urllib.parse

class LoginView(TemplateView,InflowLoginView):
    template_name = "login.html"
    
    def get(self, request):
        logout(request)
        context = { "linkedin" : self.set_linkedin_params() }
        
        # If this page was hit from LinkedIn, go ahead and handle to log the user in
        if self.is_this_a_linkedin_request(request):
            return self.handle_linkedin_request(request)
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = { "linkedin" : self.set_linkedin_params() }
        
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

class UserDashboardView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class BaseSitemap(Sitemap):
    def items(self):
        return ["login",
                "accounts:create",
                "htmldemos:demo_home",
                "htmldemos:freelancer_active_use",
                "htmldemos:freelancer_active_use_quick_view",
                "htmldemos:freelancer_active_use_specific_project_milestones",
                "htmldemos:freelancer_active_use_specific_project_overview",
                "htmldemos:freelancer_active_use_specific_project_invoices",
                "htmldemos:freelancer_active_use_specific_project_files",
                "htmldemos:freelancer_active_use_specific_project_milestones_upload_idle",
                "htmldemos:freelancer_active_use_specific_project_milestones_upload_progress",
                "htmldemos:freelancer_active_use_specific_project_milestones_preview",
                "htmldemos:freelancer_active_use_specific_project_milestones_preview_note",
                "htmldemos:freelancer_active_use_specific_project_milestones_schedule",
                "htmldemos:freelancer_active_use_specific_project_milestones_schedule_send",
                "htmldemos:freelancer_active_use_specific_project_milestones_schedule_send_now",
                "htmldemos:freelancer_active_use_email_confirm_freelancer",
                "htmldemos:freelancer_active_use_email_confirm_client",
                "htmldemos:client_active_use",
                "htmldemos:client_active_use_projects_home",
                "htmldemos:client_active_use_projects_quick_view",
                "htmldemos:client_active_use_projects_milestones",
                "htmldemos:client_active_use_projects_overview",
                "htmldemos:client_active_use_projects_invoices",
                "htmldemos:client_active_use_projects_files",
                "htmldemos:client_active_use_projects_preview",
                "htmldemos:contract_creation",
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