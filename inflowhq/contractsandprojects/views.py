from __future__ import unicode_literals
from django.http import Http404
from django.core.exceptions import PermissionDenied
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
            
            appended_project = { "id" : contract.id, "project_title" : contract.Name, "progress" : contract.get_contract_state_view(), "start_date" : contract.StartDate.strftime("%b %d %Y"), "end_date": contract.EndDate.strftime("%b %d %Y") }
            
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
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        action_taken = request.POST.get("action", "")
        
        if action_taken == "Continue": # User wants to go to the next step
            self.process_continue(request,**kwargs)
            return redirect(reverse("contracts:home"))
        elif action_taken == "Save for Later":
            self.process_save_for_later(request,**kwargs)
            return redirect(reverse("contracts:home"))
        else:
            # Going to somehow need to handle this one way or another
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(CreateContractStepOne, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        
        # Used for sending contract information to the view
        contract_info = { 
            "id" : 0, "contract_name" : "", "contract_description" : "", "contract_type" : "d", "ownership_type" : "i",
            "contact" : { "name" : "", "billing_name" : "", "email" : "", "phone_1" : "", "phone_2" : "", "phone_3" : "" },
            "locations" : []
        }
        
        if "contract_id" in kwargs:
            selected_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            
            if selected_contract is None: # Just exit and raise a 404 message
                raise Http404()
            
            selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
            
            if selected_contract.does_this_user_have_permission_to_see_contract(request.user):
                selected_recipient_addresses = RecipientAddress.objects.filter(RecipientForAddress=selected_recipient)
                contract_info["id"] = selected_contract.id
                contract_info["contract_name"] = selected_contract.Name
                contract_info["contract_description"] = selected_contract.Description
                contract_info["contract_type"] = selected_contract.ContractType
                contract_info["ownership_type"] = selected_contract.Ownership
                
                if selected_recipient is not None:
                    contract_info["contact"]["name"] = selected_recipient.Name
                    contract_info["contact"]["billing_name"] = selected_recipient.BillingName
                    contract_info["contact"]["email"] = selected_recipient.EmailAddress
                    
                    # Fracture the phone number
                    if selected_recipient.PhoneNumber != "" and selected_recipient.PhoneNumber is not None:
                        number_parts = selected_recipient.PhoneNumber.split("-")
                        contract_info["contact"]["phone_1"] = number_parts[0]
                        contract_info["contact"]["phone_2"] = number_parts[1]
                        contract_info["contact"]["phone_3"] = number_parts[2]
                    
                    # Iterate through all locations and put them into the JSON context
                    addr_index = 1
                    for address in selected_recipient_addresses:
                        entered_address = { "index" : addr_index, "addr1" : address.Address1, "addr2" : address.Address2, "city" : address.City, "state" : address.State }
                        contract_info["locations"].append(entered_address)
                        addr_index = addr_index + 1
                
            else:
                raise PermissionDenied() # Raise 403
        
        context["contract_info"] = contract_info
        return context
    
    def process_continue(self,request,**kwargs):
        self.build_new_object(request,**kwargs)
    
    def process_save_for_later(self,request,**kwargs):
        self.build_new_object(request,**kwargs)
        
    def build_new_object(self,request,**kwargs):
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
        
        # Create a brand new Contract or go ahead and edit an existing one
        if "contract_id" in kwargs:
            created_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            
            if created_contract is None:
                created_contract = Contract.objects.create(Creator=request.user,Name=project_name,ContractType=contract_type_db,Ownership=who_owns_db)
            else:
                created_contract.Name = project_name
                created_contract.ContractType = contract_type_db
                created_contract.Ownership = who_owns_db
        else:
            created_contract = Contract.objects.create(Creator=request.user,Name=project_name,ContractType=contract_type_db,Ownership=who_owns_db)
        
        if description != "":
            created_contract.Description = description
        
        created_contract.create_slug()
        created_contract.save()
        
        # Build Relationship
        if not Relationship.objects.filter(ContractUser=request.user,ContractForRelationship=created_contract).exists():
            Relationship.objects.create(ContractUser=request.user,ContractForRelationship=created_contract,RelationshipType='f')
        
        # Build Recipient Information
        company_name = request.POST.get("company-name", "")
        client_billing_name = request.POST.get("client-billing-name", "")
        client_email = request.POST.get("client-email", "")
        phone_area_1 = request.POST.get("phone-area-1", "")
        phone_area_2 = request.POST.get("phone-area-2", "")
        phone_area_3 = request.POST.get("phone-area-3", "")
        
        # Handle the need to update Recipient
        created_contract_recipient = Recipient.objects.filter(ContractForRecipient=created_contract).first()
        if created_contract_recipient is None:
            created_contract_recipient = Recipient.objects.create(ContractForRecipient=created_contract,BillingName=client_billing_name,EmailAddress=client_email)
        else:
            created_contract_recipient.BillingName = client_billing_name
            created_contract_recipient.EmailAddress = client_email
        
        if company_name != "":
            created_contract_recipient.Name = company_name
        if phone_area_1 != "" and phone_area_2 != "" and phone_area_3 != "":
            created_contract_recipient.PhoneNumber = ("%s-%s-%s" % (phone_area_1, phone_area_2, phone_area_3))
        
        created_contract_recipient.save()
        
        # Build Recipient Address
        retrieved_contract_recipient_addresses = RecipientAddress.objects.filter(RecipientForAddress=created_contract_recipient)
        
        client_business_address_1 = request.POST.getlist("client-business-address-1")
        client_business_address_2 = request.POST.getlist("client-business-address-2")
        client_business_address_city = request.POST.getlist("client-business-address-city")
        client_business_address_state = request.POST.getlist("client-business-address-state")
        
        for address_index in range(0,len(client_business_address_1)):
            if address_index < len(retrieved_contract_recipient_addresses):
                created_contract_recipient_address = retrieved_contract_recipient_addresses[address_index]
            else:
                created_contract_recipient_address = created_contract_recipient.create_address_for_recipient()
                
            created_contract_recipient_address.Address1 = client_business_address_1[address_index]
            created_contract_recipient_address.Address2 = client_business_address_2[address_index]
            created_contract_recipient_address.City = client_business_address_city[address_index]
            created_contract_recipient_address.State = client_business_address_state[address_index]
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