from __future__ import unicode_literals
import datetime
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse
from accounts.models import UserSettings
from contractsandprojects.models import Contract, Recipient, RecipientAddress, Relationship, Milestone
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
            return self.process_continue(request,**kwargs)
        elif action_taken == "Save for Later":
            return self.process_save_for_later(request,**kwargs)
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
                        contract_info["contact"]["phone_1"] = number_parts[0].__str__()
                        contract_info["contact"]["phone_2"] = number_parts[1].__str__()
                        contract_info["contact"]["phone_3"] = number_parts[2].__str__()
                    
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
        created_contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:create_contract_step_2", kwargs={"contract_id" : created_contract.id}))
    
    def process_save_for_later(self,request,**kwargs):
        created_contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:home"))
        
    def build_new_object(self,request,**kwargs):
        # Build Contract
        project_name = request.POST.get("contractName", "")
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
        client_billing_name = request.POST.get("companyBillingName", "")
        client_email = request.POST.get("companyContactEmail", "")
        phone_area_1 = request.POST.get("phoneArea1", "")
        phone_area_2 = request.POST.get("phoneArea2", "")
        phone_area_3 = request.POST.get("phoneArea3", "")
        
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
        
        client_business_address_1 = request.POST.getlist("clientBusinessAddress1")
        client_business_address_2 = request.POST.getlist("clientBusinessAddress2")
        client_business_address_city = request.POST.getlist("clientBusinessAddressCity")
        client_business_address_state = request.POST.getlist("clientBusinessAddressState")
        
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
        
        return created_contract

class CreateContractStepTwo(LoginRequiredMixin, TemplateView):
    template_name = "contract.creation.second.step.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        action_taken = request.POST.get("action", "")
        
        if action_taken == "Continue": # User wants to go to the next step
            return self.process_continue(request,**kwargs)
        elif action_taken == "Save for Later":
            return self.process_save_for_later(request,**kwargs)
        else:
            # Going to somehow need to handle this one way or another
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(CreateContractStepTwo, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        context["in_edit_mode"] = False
        
        today = datetime.date.today()
        # Used for sending contract information to the view
        contract_info = { 
            "id" : 0, "contract_name" : "", "start_date" : today.strftime("%b %d %Y"), "end_date" : today.strftime("%b %d %Y"), "type" : "d",
            "milestones" : []
        }
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if "contract_id" in kwargs:
            selected_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            
            if selected_contract is None: # Just exit and raise a 404 message
                raise Http404()
            else:
                context["in_edit_mode"] = True
                
                if selected_contract.does_this_user_have_permission_to_see_contract(request.user):
                    contract_info["id"] = selected_contract.id
                    contract_info["contract_name"] = selected_contract.Name
                    contract_info["start_date"] = selected_contract.StartDate.strftime("%b %d %Y")
                    contract_info["end_date"] = selected_contract.EndDate.strftime("%b %d %Y")
                    contract_info["type"] = selected_contract.ContractType
                    
                    # Retrieve the milestones (if any)
                    milestone_index = 1
                    selected_contract_milestones = Milestone.objects.filter(MilestoneContract=selected_contract)
                    for milestone in selected_contract_milestones:
                        entered_milestone = { "index" : milestone_index, "name" : milestone.Name, "description" : milestone.Explanation, "estimateHourCompletion" : milestone.EstimateHoursRequired, "totalMilestoneAmount" : milestone.MilestonePaymentAmount, "milestoneDeadline" : milestone.Deadline.strftime("%b %d %Y") }
                        milestone_index = milestone_index + 1
                        contract_info["milestones"].append(entered_milestone)
                else:
                    raise PermissionDenied() # Raise 403
        
        context["contract_info"] = contract_info
        return context
    
    def process_continue(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:home"))
    
    def process_save_for_later(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:home"))
        
    def build_new_object(self,request,**kwargs):
        # Build Contract Details
        contractStartDate = request.POST.get("contractStartDate", "")
        contractEndDate = request.POST.get("contractEndDate", "")
        hourlyRate = request.POST.get("hourlyRate", "")
        milestoneAmount = request.POST.get("milestoneAmount", "")
        downPaymentAmount = request.POST.get("downPaymentAmount", "")
        totalNumberOfRevisions = request.POST.get("totalNumberOfRevisions", "")
        
        # Milestone amounts
        milestoneName = request.POST.getlist("milestoneName")
        milestoneDescription = request.POST.getlist("milestoneDescription")
        milestonesEstimateHours = request.POST.getlist("milestonesEstimateHours")
        milestoneAmount = request.POST.getlist("milestoneAmount")
        milestoneDeadline = request.POST.getlist("milestoneDeadline")
        
        created_contract = None
        if "contract_id" in kwargs:
            created_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            print(created_contract)
            created_contract.StartDate = datetime.datetime.strptime(contractStartDate, "%b %d %Y")
            created_contract.EndDate = datetime.datetime.strptime(contractEndDate, "%b %d %Y")
            created_contract.save()
            print("Saved Contract")
            
        return created_contract
    
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