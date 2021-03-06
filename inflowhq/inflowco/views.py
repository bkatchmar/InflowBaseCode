from __future__ import unicode_literals # I have no idea what this even is
# References from our own library
from accounts.inflowaccountloginview import InflowLoginView
from accounts.models import UserSettings
from contractsandprojects.models import Milestone, Recipient, Relationship
from inflowco.models import Currency, EmailSignup
from inflowco.mailchimp import MailChimpCommunication
from easy_pdf.views import PDFTemplateView
# Django references
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
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
            email_lookup = EmailSignup.objects.filter(Address=entered_email_address,Group="g")
            
            if len(email_lookup) == 0:
                mailchimp_comm = MailChimpCommunication()
                mailchimp_comm.post_email_to_list(settings.MAILCHIMP_LIST["General Splash Page Signups"],entered_email_address)
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
            email_lookup = EmailSignup.objects.filter(Address=entered_email_address,Group="g")
            
            if len(email_lookup) == 0:
                mailchimp_comm = MailChimpCommunication()
                mailchimp_comm.post_email_to_list(settings.MAILCHIMP_LIST["General Splash Page Signups"],entered_email_address)
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
        
        user_settings = UserSettings()
        user_settings = user_settings.get_settings_based_on_user(request.user)
        
        user_contracts_where_relationship_exists = Relationship.objects.filter(ContractUser=request.user)
        all_recipients = Recipient.objects.all()
        all_milestones = Milestone.objects.all().order_by("Deadline")
        
        context["needs_stripe"] = user_settings.does_this_user_need_stripe()
        context["call_state"] = settings.STRIPE_CALL_STATE
        context["stripe_acct"] = settings.STRIPE_ACCOUNT_ID
        context["first_name"] = request.user.first_name
        context["projects_in_progress"] = []
        context["upcoming_milestones"] = []
        
        for relationship in user_contracts_where_relationship_exists:
            if relationship.ContractForRelationship.StartDate <= timezone.now().date() and relationship.ContractForRelationship.EndDate >= timezone.now().date():
                # Get recipient and fill in entry for the in progress projects
                recipient_for_contract = all_recipients.filter(ContractForRecipient=relationship.ContractForRelationship).first()
                context["projects_in_progress"].append({ "name" : relationship.ContractForRelationship.Name, "progress" : relationship.ContractForRelationship.get_contract_state_view(), "client" : recipient_for_contract.Name })
                
                # Get milestones for this contract that are still due
                contract_milestones = all_milestones.filter(MilestoneContract=relationship.ContractForRelationship)
                
                for milestone in contract_milestones:
                    if milestone.Deadline >= timezone.now().date():
                        context["upcoming_milestones"].append({ "date" : milestone.Deadline.strftime("%b %d %Y"), "name" : milestone.Name, "project" : milestone.MilestoneContract.Name, "amount" : "{0:.2f}".format(milestone.MilestonePaymentAmount) })
        
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
        return ["index","how_it_works","about_us","accounts:login","accounts:create"]

    def location(self, item):
        return reverse(item)
    
    def changefreq(self, item):
        return "never"
        
    def priority(self, item):
        if item == "index":
            return 1.0
        elif item == "how_it_works":
            return 0.9
        elif item == "about_us":
            return 0.7
        elif item == "accounts:login":
            return 0.1
        elif item == "accounts:create":
            return 0.1
        else:
            return 0.5
    
class GoogleDomainVerificationFile(TemplateView):
    template_name = "google255e09f84b6b193b.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DjangoModelJsonResponse(View):
    def get(self, request):
        first_currency = Currency.objects.first()
        return JsonResponse(first_currency.to_dict(), safe=False)