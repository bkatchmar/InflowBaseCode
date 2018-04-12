from __future__ import unicode_literals
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse
from accounts.models import UserSettings
from contractsandprojects.models import Contract, Recipient, RecipientAddress, Relationship
from contractsandprojects.models import CONTRACT_TYPES
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
        
        user_created_contracts = Contract.objects.filter(Creator=request.user)
        
        # Build the projects JSON object for the view
        for contract in user_created_contracts:
            recipient_for_contract = Recipient.objects.filter(ContractForRecipient=contract).first()
            
            appended_project = { "project_title" : contract.Name, "progress" : contract.get_contract_state_view(), "start_date" : contract.StartDate.strftime("%b %d %Y"), "end_date": contract.EndDate.strftime("%b %d %Y") }
            
            if recipient_for_contract is None:
                appended_project["project_client"] = ""
            else:
                appended_project["project_client"] = recipient_for_contract.BillingName
                
            context["projects"].append(appended_project)
        
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
        
        if action_taken == "Continue": # User wants to go to the next step
            self.process_continue(request)
            return redirect(reverse("contracts:home"))
        elif action_taken == "Save for Later":
            self.process_save_for_later(request)
            return redirect(reverse("contracts:home"))
        else:
            # Going to somehow need to handle this one way or another
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        # Set the context
        context = super(CreateContractStepOne, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        return context
    
    def process_continue(self,request):
        self.build_new_object(request)
    
    def process_save_for_later(self,request):
        self.build_new_object(request)
        
    def build_new_object(self,request):
        # Build Contract
        project_name = request.POST.get("project-name", "")
        contract_type = request.POST.get("contract-type", "")
        contract_type_db = ""
        description = request.POST.get("description", "")
        who_owns = request.POST.get("who-owns", "")
        who_owns_db = ""
        
        if contract_type == "milestones":
            contract_type_db = "d"
        else:
            contract_type_db = "t"
            
        if who_owns == "myself":
            who_owns_db = "i"
        else:
            who_owns_db = "u"
        
        created_contract = Contract.objects.create(Creator=request.user,Name=project_name,ContractType=contract_type_db,Ownership=who_owns_db)
        if description != "":
            created_contract.Description = description
        created_contract.create_slug()
        created_contract.save()
        
        # Build Relationship
        Relationship.objects.create(ContractUser=request.user,ContractForRelationship=created_contract,RelationshipType='f')
        
        # Build Recipient Information
        company_name = request.POST.get("company-name", "")
        client_billing_name = request.POST.get("client-billing-name", "")
        client_email = request.POST.get("client-email", "")
        phone_area_1 = request.POST.get("phone-area-1", "")
        phone_area_2 = request.POST.get("phone-area-2", "")
        phone_area_3 = request.POST.get("phone-area-3", "")
        
        created_contract_recipient = Recipient.objects.create(ContractForRecipient=created_contract,BillingName=client_billing_name,EmailAddress=client_email)
        
        if company_name != "":
            created_contract_recipient.Name = company_name
        if phone_area_1 != "" and phone_area_2 != "" and phone_area_3 != "":
            created_contract_recipient.PhoneNumber = ("%s-%s-%s" % (phone_area_1, phone_area_2, phone_area_3))
        
        created_contract_recipient.save()
        
        # Build Recipient Address
        client_business_address_1_1 = request.POST.get("client-business-address-1-1", "")
        client_business_address_2_1 = request.POST.get("client-business-address-2-1", "")
        client_business_address_city_1 = request.POST.get("client-business-address-city-1", "")
        client_business_address_state_1 = request.POST.get("client-business-address-state-1", "")
        
        created_contract_recipient_address = created_contract_recipient.create_address_for_recipient()
        
        created_contract_recipient_address.Address1 = client_business_address_1_1
        created_contract_recipient_address.Address2 = client_business_address_2_1
        created_contract_recipient_address.City = client_business_address_city_1
        created_contract_recipient_address.State = client_business_address_state_1
        created_contract_recipient_address.save()
    
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