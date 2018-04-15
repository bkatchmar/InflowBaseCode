from __future__ import unicode_literals # I have no idea what this even is
# References from our own library
from accounts.inflowaccountloginview import InflowLoginView
from inflowco.models import Currency, EmailSignup
from easy_pdf.views import PDFTemplateView
# Django references
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

# Error Pages
def resource_unauthorized(request, exception, template_name="errors/403.html"):
    return render(request, template_name)

def server_error(request, template_name="errors/500.html"):
    return render(request, template_name)
 
def not_found(request, exception, template_name="errors/404.html"):
    return render(request, template_name)

class IndexView(TemplateView):
    template_name = "index.html"
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["active_link"] = "home"
        return context
    
    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request):
        context = self.get_context_data()
        
        entered_email_address = request.POST.get("email-address", "")
        
        if entered_email_address != "":
            EmailSignup.objects.create(Address=entered_email_address,Group="g")
            context["sign_up_msg"] = "Thank You For Signing Up"
        
        return render(request, self.template_name, context)

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
    
class HowItWorksView(TemplateView):
    template_name = "how-it-works.html"
    
    def get_context_data(self, **kwargs):
        context = super(HowItWorksView, self).get_context_data(**kwargs)
        context["active_link"] = "how it works"
        return context
    
    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request):
        context = self.get_context_data()
        
        entered_email_address = request.POST.get("email-address", "")
        
        if entered_email_address != "":
            EmailSignup.objects.create(Address=entered_email_address,Group="g")
            context["sign_up_msg"] = "Thank You For Signing Up"
        
        return render(request, self.template_name, context)

class AboutUsView(TemplateView):
    template_name = "about-us.html"
    
    def get_context_data(self, **kwargs):
        context = super(AboutUsView, self).get_context_data(**kwargs)
        context["active_link"] = "about us"
        return context

class BlogHomeView(TemplateView):
    template_name = "blog.home.html"
    
    def get_context_data(self, **kwargs):
        context = super(BlogHomeView, self).get_context_data(**kwargs)
        context["active_link"] = "blog"
        return context
    
    def get(self, request):
        return redirect("https://medium.com/@InFlowHQ")
    
    def post(self, request):
        return redirect("https://medium.com/@InFlowHQ")

class SavePdfTrials(PDFTemplateView):
    template_name = "basepdftemplate.html"
    
class UserDashboardLowFi(LoginRequiredMixin,TemplateView):
    template_name = "user.dashboard.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def get_context_data(self, request, **kwargs):
        context = super(UserDashboardLowFi, self).get_context_data(**kwargs)
        context["first_name"] = request.user.first_name
        return context

class HelpCenter(LoginRequiredMixin,TemplateView):
    template_name = "help.center.html"
    
    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(HelpCenter, self).get_context_data(**kwargs)
        return context
    
class HelpTopicInflow101(LoginRequiredMixin,TemplateView):
    template_name = "help.topic.inflow.101.html"
    
    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(HelpTopicInflow101, self).get_context_data(**kwargs)
        return context
    
class BaseSitemap(Sitemap):
    def items(self):
        return ["index",
                "how_it_works",
                "about_us",
                "accounts:login",
                "accounts:create",
                "htmldemos:freelancer_active_use_specific_project_milestones_upload_idle",
                "htmldemos:freelancer_active_use_specific_project_milestones_upload_progress",
                "htmldemos:freelancer_active_use_specific_project_milestones_preview_note",
                "htmldemos:freelancer_active_use_specific_project_milestones_preview",
                "htmldemos:freelancer_active_use_specific_project_milestones_schedule_send_now",
                "htmldemos:freelancer_active_use_specific_project_milestones_schedule_send",
                "htmldemos:freelancer_active_use_specific_project_milestones_schedule",
                "htmldemos:freelancer_active_use_specific_project_milestones",
                "htmldemos:freelancer_active_use_specific_project_overview",
                "htmldemos:freelancer_active_use_specific_project_invoices",
                "htmldemos:freelancer_active_use_specific_project_files",
                "htmldemos:freelancer_active_use_quick_view",
                "htmldemos:freelancer_active_use_email_confirm_freelancer",
                "htmldemos:freelancer_active_use_email_confirm_client",
                "htmldemos:freelancer_active_use",
                "htmldemos:client_active_use_projects_preview_accept_send",
                "htmldemos:client_active_use_projects_preview_accept",
                "htmldemos:client_active_use_projects_preview_decline_send",
                "htmldemos:client_active_use_projects_preview_decline",
                "htmldemos:client_active_use_projects_preview",
                "htmldemos:client_active_use_projects_files",
                "htmldemos:client_active_use_projects_invoices",
                "htmldemos:client_active_use_projects_overview",
                "htmldemos:client_active_use_projects_milestones",
                "htmldemos:client_active_use_projects_quick_view",
                "htmldemos:client_active_use_projects_home",
                "htmldemos:client_active_use",
                "htmldemos:contract_creation_lump_sum",
                "htmldemos:contract_creation_hourly",
                "htmldemos:contract_creation_extra_fees",
                "htmldemos:contract_overview_lump_sum",
                "htmldemos:contract_overview_hourly",
                "htmldemos:contract_overview_preview_send",
                "htmldemos:contract_overview_final",
                "htmldemos:contract_creation"]

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

class BasicJsonResponse(View):
    def get(self, request):
        data = {
            'name': 'Vitor',
            'location': 'Finland',
            'is_active': True,
            'count': 28
            }
        return JsonResponse(data)

class DjangoModelJsonResponse(View):
    def get(self, request):
        first_currency = Currency.objects.first()
        data = {
            "IdCurrency" : first_currency.IdCurrency,
            "Country" : first_currency.Country,
            "Name" : first_currency.Name,
            "Code" : first_currency.Code
            }
        return JsonResponse(first_currency.to_dict(), safe=False)