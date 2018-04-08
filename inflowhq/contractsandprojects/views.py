from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.models import UserSettings
from contractsandprojects.models import Contract
from contractsandprojects.email_handler import EmailHandler

class ContractCreationView(LoginRequiredMixin, TemplateView):
    template_name = "projects.home.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Get some necessary User Information
        settings = UserSettings()
        settings = settings.get_settings_based_on_user(request.user)
        
        # Set the context
        context = super(ContractCreationView, self).get_context_data(**kwargs)
        context["projects"] = []
        context["view_mode"] = "projects"
        
        if settings.StripeConnectAccountKey is None:
            context["needs_stripe"] = True
        else:
            context["needs_stripe"] = False
        
        return context

class MyContactsView(LoginRequiredMixin, TemplateView):
    template_name = "projects.contacts.html"
    
    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        # Set the context
        context = super(MyContactsView, self).get_context_data(**kwargs)
        context["view_mode"] = "contacts"
        return context

class CreateContractStepOne(LoginRequiredMixin, TemplateView):
    template_name = "contract.creation.first.step.html"
    
    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = self.get_context_data()
        
        action_taken = request.POST.get("action", "")
        # Back
        # Continue
        # Save for Later
        print(action_taken)
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        # Set the context
        context = super(CreateContractStepOne, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        return context
    
class EmailPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "email_area.html"
    
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        
        # Objects we are going to use to send our emails
        contract_to_send = Contract()
        handler = EmailHandler()
        
        email_mode = request.POST.get("mode", "")
        handler.send_base_email(contract_to_send)
        return render(request, self.template_name, context)