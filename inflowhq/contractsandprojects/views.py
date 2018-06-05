from __future__ import unicode_literals
from accounts.signupvalidation import ClientAccountGenerator
import datetime
import json
import os
import pathlib

# Django References
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse

# Accounts App References
from accounts.models import UserSettings

# Contracts and Projects App References
from contractsandprojects.contract_standard_permission_handler import ContractPermissionHandler
from contractsandprojects.models import Contract, ContractFile, Recipient, RecipientAddress, Relationship, Milestone, MilestoneFile
from contractsandprojects.models import CONTRACT_TYPES
from contractsandprojects.email_handler import EmailHandler
from contractsandprojects.request_handler import AmazonBotoHandler, RequestInputHandler

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
        
        user_contracts_where_relationship_exists = Relationship.objects.filter(ContractUser=request.user)
        all_recipients = Recipient.objects.all()
        
        # Build the projects JSON object for the view
        for relationship in user_contracts_where_relationship_exists:
            contract = relationship.ContractForRelationship
            recipient_for_contract = all_recipients.filter(ContractForRecipient=contract).first()
            
            appended_project = { "id" : contract.id, "project_title" : contract.Name, "progress" : contract.get_contract_state_view(), "start_date" : contract.StartDate.strftime("%b %d %Y"), "end_date": contract.EndDate.strftime("%b %d %Y"), "state" : contract.ContractState, "slug" : contract.UrlSlug, "relationship" : relationship.RelationshipType }
            
            if recipient_for_contract is None:
                appended_project["project_client"] = ""
            else:
                appended_project["project_client"] = recipient_for_contract.BillingName
                
            context["projects"].append(appended_project)
        
        context["view_mode"] = "projects"
        context["needs_stripe"] = (not settings.can_this_user_create_contract())
        
        return context

class MyContactsView(LoginRequiredMixin, TemplateView):
    template_name = "projects.contacts.html"
    
    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        total_recipients = []
        iterator = 1
        
        # Set the context
        context = super(MyContactsView, self).get_context_data(**kwargs)
        context["view_mode"] = "contacts"
        
        user_contracts = Contract.objects.filter(Creator=request.user)
        
        for contract in user_contracts:
            recipients = Recipient.objects.filter(ContractForRecipient=contract)
            
            for r in recipients:
                context_append = { "index": iterator, "recipient" : r, "addresses" : [] }
                
                recipient_address = RecipientAddress.objects.filter(RecipientForAddress=r)
                
                for addr in recipient_address:
                    context_append["addresses"].append(addr)
                
                total_recipients.append(context_append)
                iterator = iterator + 1
        
        context["contacts"] = total_recipients
        return context

class CreateContractStepOne(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "contract_creation/contract.creation.first.step.html"
    
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
        context = super(CreateContractStepOne, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        context["in_edit_mode"] = True
        
        # Used for sending contract information to the view
        contract_info = { 
            "id" : 0, "contract_name" : "", "contract_description" : "", "contract_type" : "d", "ownership_type" : "i",
            "contact" : { "name" : "", "billing_name" : "", "email" : "", "phone" : "" },
            "locations" : []
        }
        
        selected_contract = self.get_contract_if_user_is_creator(request.user,**kwargs)
        
        if selected_contract is not None:
            selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
            selected_recipient_addresses = RecipientAddress.objects.filter(RecipientForAddress=selected_recipient)
            context["in_edit_mode"] = (selected_contract.ContractState == "c")
            
            contract_info["id"] = selected_contract.id
            contract_info["contract_name"] = selected_contract.Name.replace("\"", "\\\"").replace("'", "\\'")
            
            if selected_contract.Description is not None:
                contract_info["contract_description"] = selected_contract.Description.replace("\"", "\\\"").replace("'", "\\'")
            else:
                contract_info["contract_description"] = ""
            
            contract_info["contract_type"] = selected_contract.ContractType
            contract_info["ownership_type"] = selected_contract.Ownership
            
            if selected_recipient is not None:
                contract_info["contact"]["name"] = selected_recipient.Name
                contract_info["contact"]["billing_name"] = selected_recipient.BillingName
                contract_info["contact"]["email"] = selected_recipient.EmailAddress
                
                # Fracture the phone number
                if selected_recipient.PhoneNumber != "" and selected_recipient.PhoneNumber is not None:
                    number_parts = selected_recipient.PhoneNumber.split("-")
                    contract_info["contact"]["phone"] = selected_recipient.PhoneNumber
                    
                # Iterate through all locations and put them into the JSON context
                addr_index = 1
                for address in selected_recipient_addresses:
                    entered_address = { "index" : addr_index, "addr1" : address.Address1, "addr2" : address.Address2, "city" : address.City, "state" : address.State }
                    contract_info["locations"].append(entered_address)
                    addr_index = addr_index + 1
            
            if len(selected_recipient_addresses) == 0:
                contract_info["locations"].append({"index":1,"addr1":"","addr2":"","city":"","state":""})
        else:
            contract_info["locations"].append({"index":1,"addr1":"","addr2":"","city":"","state":""})
                    
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
                created_contract = Contract.objects.create(Creator=request.user,Name=project_name,ContractType=contract_type_db,Ownership=who_owns_db,StartDate=datetime.date.today(),EndDate=datetime.date.today())
            else:
                created_contract.Name = project_name
                created_contract.ContractType = contract_type_db
                created_contract.Ownership = who_owns_db
        else:
            created_contract = Contract.objects.create(Creator=request.user,Name=project_name,ContractType=contract_type_db,Ownership=who_owns_db,StartDate=datetime.date.today(),EndDate=datetime.date.today())
        
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
        phone_number = request.POST.get("phoneNumber", "")
        
        # Handle the need to update Recipient
        created_contract_recipient = Recipient.objects.filter(ContractForRecipient=created_contract).first()
        if created_contract_recipient is None:
            created_contract_recipient = Recipient.objects.create(ContractForRecipient=created_contract,BillingName=client_billing_name,EmailAddress=client_email,PhoneNumber=phone_number)
        else:
            created_contract_recipient.BillingName = client_billing_name
            created_contract_recipient.EmailAddress = client_email
            created_contract_recipient.PhoneNumber = phone_number
        
        if company_name != "":
            created_contract_recipient.Name = company_name
        
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

class CreateContractStepTwo(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "contract_creation/contract.creation.second.step.html"
    
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
            "id" : 0, "contract_name" : "", "start_date" : today.strftime("%b %d %Y"), "end_date" : today.strftime("%b %d %Y"), "type" : "d", "contract_total" : 0.00, "down_payment_amount" : 0.00, "total_revisions" : 1, "hourly_rate" : 0.00,
            "milestones" : []
        }
        
        selected_contract = self.get_contract_if_user_is_creator(request.user,**kwargs)
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if selected_contract is not None:
            context["in_edit_mode"] = (selected_contract.ContractState == "c")
            contract_info["id"] = selected_contract.id
            contract_info["contract_name"] = selected_contract.Name
            contract_info["start_date"] = selected_contract.StartDate.strftime("%b %d %Y")
            contract_info["end_date"] = selected_contract.EndDate.strftime("%b %d %Y")
            contract_info["type"] = selected_contract.ContractType
            contract_info["contract_total"] = selected_contract.TotalContractWorth
            contract_info["down_payment_amount"] = selected_contract.DownPaymentAmount
            contract_info["total_revisions"] = selected_contract.NumberOfAllowedRevisions
            contract_info["hourly_rate"] = selected_contract.HourlyRate
            
            # Retrieve the milestones (if any)
            milestone_index = 0
            selected_contract_milestones = Milestone.objects.filter(MilestoneContract=selected_contract)
            for milestone in selected_contract_milestones:
                entered_milestone = { "index" : milestone_index, "id" : milestone.IdMilestone, "front_index": (milestone_index+1), "name" : milestone.Name, "description" : milestone.Explanation, "estimateHourCompletion" : milestone.EstimateHoursRequired, "totalMilestoneAmount" : milestone.MilestonePaymentAmount, "milestoneDeadline" : milestone.Deadline.strftime("%b %d %Y") }
                milestone_index = milestone_index + 1
                contract_info["milestones"].append(entered_milestone)
                
            if milestone_index == 0:
                entered_milestone = { "index":milestone_index,"id":0,"front_index":(milestone_index+1),"name":"","description":"","estimateHourCompletion":0,"totalMilestoneAmount":0,"milestoneDeadline":"" }
                milestone_index = milestone_index + 1
                contract_info["milestones"].append(entered_milestone)

            contract_info["number_of_milestones"] = milestone_index
        
        context["contract_info"] = contract_info
        return context
    
    def process_continue(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:create_contract_step_3", kwargs={"contract_id" : contract.id}))
    
    def process_save_for_later(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:home"))
        
    def build_new_object(self,request,**kwargs):
        # Build Contract Details
        contractStartDate = request.POST.get("contractStartDate", "")
        contractEndDate = request.POST.get("contractEndDate", "")
        hourlyRate = request.POST.get("hourlyRate", "")
        downPaymentAmount = request.POST.get("downPaymentAmount", "")
        totalNumberOfRevisions = request.POST.get("totalNumberOfRevisions", "")
        totalContractAmount = request.POST.get("totalContractAmount", "")
        
        # Milestone amounts
        milestoneName = request.POST.getlist("milestoneName")
        milestoneDescription = request.POST.getlist("milestoneDescription")
        milestonesEstimateHours = request.POST.getlist("milestonesEstimateHours")
        milestoneAmount = request.POST.getlist("milestoneAmount")
        milestoneDeadline = request.POST.getlist("milestoneDeadline")
        milestone_id = request.POST.getlist("milestoneId", "")
        milestone_needs_to_be_removed = request.POST.getlist("removeMilestone", "")
        
        handler = RequestInputHandler()
        
        created_contract = None
        if "contract_id" in kwargs:
            created_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            created_contract.StartDate = handler.get_entry_for_date(contractStartDate)
            created_contract.EndDate = handler.get_entry_for_date(contractEndDate)
            
            created_contract.TotalContractWorth = handler.get_entry_for_float(totalContractAmount)
            created_contract.DownPaymentAmount = handler.get_entry_for_float(downPaymentAmount)
            created_contract.HourlyRate = handler.get_entry_for_float(hourlyRate)
            created_contract.NumberOfAllowedRevisions = handler.get_entry_for_int(totalNumberOfRevisions)
            
            created_contract.save()
            
            retrieved_milestones = Milestone.objects.filter(MilestoneContract=created_contract)
            
            # Build Each Milestone Object
            for milestone_index in range(0,len(milestoneName)):
                i_am_removing_this_milestone = (milestone_needs_to_be_removed[milestone_index]=="true")
                
                if i_am_removing_this_milestone:
                    created_contract.delete_milestone_if_exists(int(milestone_id[milestone_index]))
                else:
                    if int(milestone_id[milestone_index]) == 0:
                        created_milestone = created_contract.create_new_milestone()
                    else:
                        created_milestone = retrieved_milestones.get(IdMilestone=int(milestone_id[milestone_index]))
                    
                    created_milestone.Name = milestoneName[milestone_index]
                    created_milestone.EstimateHoursRequired = handler.get_entry_for_float(milestonesEstimateHours[milestone_index])
                    created_milestone.MilestonePaymentAmount = handler.get_entry_for_float(milestoneAmount[milestone_index])
                    created_milestone.Deadline = handler.get_entry_for_date(milestoneDeadline[milestone_index])
                    
                    if milestoneDescription[milestone_index] != "":
                        created_milestone.Explanation = milestoneDescription[milestone_index]
                
                    # Now, we save the current milestone
                    created_milestone.save()
            
        return created_contract

class CreateContractStepThree(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "contract_creation/contract.creation.third.step.html"

    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        action_taken = request.POST.get("action", "")
        
        if action_taken == "Continue": # User wants to go to the next step
            return self.process_continue(request, **kwargs)
        elif action_taken == "Save for Later":
            return self.process_save_for_later(request, **kwargs)
        else:
            # Going to somehow need to handle this one way or another
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(CreateContractStepThree, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        context["in_edit_mode"] = False
        
        contract_info = { 
            "id" : 0, "contract_name" : "", "extra_revision_fee" : 0.00, "request_for_change_fee" : 0.00, "charge_for_late_review" : 0.00, "kill_fee" : 0.00,
        }
        
        selected_contract = self.get_contract_if_user_is_creator(request.user,**kwargs)
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if selected_contract is not None:
            context["in_edit_mode"] = (selected_contract.ContractState == "c")
            contract_info["id"] = selected_contract.id
            contract_info["contract_name"] = selected_contract.Name
            contract_info["extra_revision_fee"] = selected_contract.ExtraRevisionFee
            contract_info["charge_for_late_review"] = selected_contract.ChargeForLateReview
            contract_info["kill_fee"] = selected_contract.KillFee
                
        context["contract_info"] = contract_info
        return context
    
    def process_continue(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:create_contract_step_4", kwargs={"contract_id" : contract.id}))
    
    def process_save_for_later(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:home"))
    
    def build_new_object(self,request,**kwargs):
        handler = RequestInputHandler()
        extraRevisionFee = request.POST.get("extra_revision_fee", "")
        chargeLateFee = request.POST.get("charge_late_fee", "")
        killFee = request.POST.get("kill_fee", "")
        
        selected_contract = None
        if "contract_id" in kwargs:
            selected_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            selected_contract.ExtraRevisionFee = handler.get_entry_for_float(extraRevisionFee)
            selected_contract.ChargeForLateReview = handler.get_entry_for_float(chargeLateFee)
            selected_contract.KillFee = handler.get_entry_for_float(killFee)
            selected_contract.save()
        
        return selected_contract

class CreateContractStepFourth(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "contract_creation/contract.creation.fourth.step.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        action_taken = request.POST.get("action", "")
        
        if action_taken == "Continue": # User wants to go to the next step
            return self.process_continue(request, **kwargs)
        elif action_taken == "Save for Later":
            return self.process_save_for_later(request, **kwargs)
        else:
            # Going to somehow need to handle this one way or another
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(CreateContractStepFourth, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        context["in_edit_mode"] = False
        
        contract_info = {}
        
        selected_contract = self.get_contract_if_user_is_creator(request.user,**kwargs)
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if selected_contract is not None:
            context["in_edit_mode"] = (selected_contract.ContractState == "c")
            selected_contract_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
            selected_contract_recipient_addresses = RecipientAddress.objects.filter(RecipientForAddress=selected_contract_recipient)
            contract_info = selected_contract
        
        # Some quick scrubbing for the view, we're not actually saving this        
        contract_info.Name = contract_info.Name.replace("\"", "\\\"").replace("'", "\\'")
        
        if contract_info.Description is not None:
            contract_info.Description = contract_info.Description.replace("\"", "\\\"").replace("'", "\\'")
        
        context["contract_info"] = contract_info
        context["contract_recipient"] = selected_contract_recipient
        context["contract_recipient_addresses"] = selected_contract_recipient_addresses
        
        # Retrieve the milestones (if any)
        milestone_index = 1
        milestones = []
        selected_contract_milestones = Milestone.objects.filter(MilestoneContract=selected_contract)
        for milestone in selected_contract_milestones:
            entered_milestone = { "index" : milestone_index, "name" : milestone.Name.replace("\"", "\\\"").replace("'", "\\'"), "description" : milestone.Explanation.replace("\"", "\\\"").replace("'", "\\'"), "estimateHourCompletion" : milestone.EstimateHoursRequired, "totalMilestoneAmount" : milestone.MilestonePaymentAmount, "milestoneDeadline" : milestone.Deadline.strftime("%b %d %Y") }
            milestone_index = milestone_index + 1
            milestones.append(entered_milestone)
        context["milestones"] = milestones
        
        return context
    
    def process_continue(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:create_contract_step_5", kwargs={"contract_id" : contract.id}))
    
    def process_save_for_later(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:home"))
    
    def build_new_object(self,request,**kwargs):
        handler = RequestInputHandler()
        contractName = request.POST.get("contractName", "")
        contractDescription = request.POST.get("contractDescription", "")
        
        nameOfContact = request.POST.get("nameOfContact", "")
        billingName = request.POST.get("billingName", "")
        billingEmail = request.POST.get("billingEmail", "")
        phone_number = request.POST.get("phoneNumber", "")
        totalMilestoneProjectCost = request.POST.get("totalMilestoneProjectCost", "")
        totalNumberOfRevisions = request.POST.get("totalNumberOfRevisions", "")
        downPaymentAmount = request.POST.get("downPaymentAmount", "")
        extraRevisionFee = request.POST.get("extraRevisionFee", "")
        lateReviewFee = request.POST.get("lateReviewFee", "")
        killFee = request.POST.get("killFee", "")
        
        selected_contract = None
        if "contract_id" in kwargs:
            selected_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            selected_contract_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
            recipient_addresses = RecipientAddress.objects.filter(RecipientForAddress=selected_contract_recipient)
            
            selected_contract.Name = contractName
            selected_contract.Description = contractDescription
            selected_contract.TotalContractWorth = handler.get_entry_for_float(totalMilestoneProjectCost)
            selected_contract.NumberOfAllowedRevisions = handler.get_entry_for_int(totalNumberOfRevisions)
            selected_contract.DownPaymentAmount = handler.get_entry_for_float(downPaymentAmount)
            
            selected_contract.ExtraRevisionFee = handler.get_entry_for_float(extraRevisionFee)
            selected_contract.ChargeForLateReview = handler.get_entry_for_float(lateReviewFee)
            selected_contract.KillFee = handler.get_entry_for_float(killFee)
            
            selected_contract.save()
            
            if selected_contract_recipient is not None:
                selected_contract_recipient.Name = nameOfContact
                selected_contract_recipient.BillingName = billingName
                selected_contract_recipient.EmailAddress = billingEmail
                selected_contract_recipient.PhoneNumber = phone_number
                
                selected_contract_recipient.save()
                
                for addr in recipient_addresses:
                    addr1_field = ("address1%s" % addr.id)
                    addr2_field = ("address2%s" % addr.id)
                    city_field = ("addressCity%s" % addr.id)
                    state_field = ("addressState%s" % addr.id)
                    
                    address1 = request.POST.get(addr1_field, "")
                    address2 = request.POST.get(addr2_field, "")
                    city = request.POST.get(city_field, "")
                    state = request.POST.get(state_field, "")
                    
                    addr.Address1 = address1
                    addr.Address2 = address2
                    addr.City = city
                    addr.State = state
                    addr.save()
            
            # Build the milestones
            milestone_index = 1
            selected_contract_milestones = Milestone.objects.filter(MilestoneContract=selected_contract)
            for milestone in selected_contract_milestones:
                # Fields from POST
                milestoneName = request.POST.get(("milestoneName%s" % milestone_index), "")
                milestoneDescription = request.POST.get(("milestoneDescription%s" % milestone_index), "")
                milestoneTotal = request.POST.get(("milestoneTotal%s" % milestone_index), "")
                milestoneDeadline = request.POST.get(("milestoneDeadline%s" % milestone_index), "")
                estimateHourCompletion = request.POST.get(("estimateHourCompletion%s" % milestone_index), "")
                
                milestone.Name = milestoneName
                milestone.Explanation = milestoneDescription
                milestone.MilestonePaymentAmount = handler.get_entry_for_float(milestoneTotal)
                milestone.Deadline = handler.get_entry_for_date(milestoneDeadline)
                milestone.EstimateHoursRequired = handler.get_entry_for_float(estimateHourCompletion)
                milestone.save()
                
                milestone_index = milestone_index + 1
            
        return selected_contract

class CreateContractStepFive(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "contract_creation/contract.creation.fifth.step.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        action_taken = request.POST.get("action", "")
        
        if action_taken == "Send to Client": # User wants to go to the next step
            return self.process_continue(request,**kwargs)
        elif action_taken == "Save for Later":
            return self.process_save_for_later(request,**kwargs)
        else:
            # Going to somehow need to handle this one way or another
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(CreateContractStepFive, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        context["in_edit_mode"] = False
        
        selected_contract = self.get_contract_if_user_is_creator(request.user,**kwargs)
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if selected_contract is not None:
            context["in_edit_mode"] = (selected_contract.ContractState == "c")
            contract_paragraphs = selected_contract.get_contract_text()
            context["contract_info"] = selected_contract
            context["paragraphs"] = contract_paragraphs
        
        return context
    
    def process_continue(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        contract.ContractState = "u"
        contract.save()
        
        # Get Recipient information if there is one
        contract_recipient = Recipient.objects.filter(ContractForRecipient=contract).first()
        
        # Create all necessary objects for generating a relationship
        client_lookup = ClientAccountGenerator()
        client_lookup.create_relationship_for_contract(contract_recipient.EmailAddress,contract)
        
        return redirect(reverse("contracts:create_contract_step_6", kwargs={"contract_id" : contract.id}))
    
    def process_save_for_later(self,request,**kwargs):
        contract = self.build_new_object(request,**kwargs)
        return redirect(reverse("contracts:home"))
    
    def build_new_object(self,request,**kwargs):
        selected_contract = None
        if "contract_id" in kwargs:
            selected_contract = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            paragraphs = selected_contract.get_contract_text()
            
            for para in paragraphs:
                contract_text = request.POST.get(("contractParagraph%s" % para.id), "")
                para.ParagraphText = contract_text
                para.save()
                
        return selected_contract

class ContractDoneCreated(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "contract_creation/contract.message.creation-done.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        action = request.POST.get("action", "")
        
        if action=="Send to Client":
            self.create_user_and_relationship_for_contract(**kwargs)
        
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ContractDoneCreated, self).get_context_data(**kwargs)
        context["view_mode"] = "projects"
        
        selected_contract = self.get_contract_if_user_is_creator(request.user,**kwargs)
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if selected_contract is not None:
            context["in_edit_mode"] = True
            selected_contract_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
            context["contract_info"] = selected_contract
            context["contract_recipient"] = selected_contract_recipient
            context["user_email"] = request.user.email
            
            # Check if the recipient is of a user that actually exists
            client_lookup = ClientAccountGenerator()
            context["recipient_not_in_system"] = (not client_lookup.does_this_account_already_exists(selected_contract_recipient.EmailAddress))
        
        return context
    
    def create_user_and_relationship_for_contract(self, **kwargs):
        if "contract_id" in kwargs:
            selected_contract = Contract.objects.get(id=kwargs.get("contract_id"))
            selected_contract_recipient = Recipient.objects.get(ContractForRecipient=selected_contract)
            
            # Create all necessary objects for generating a relationship
            client_lookup = ClientAccountGenerator()
            client_lookup.create_relationship_for_contract(selected_contract_recipient.EmailAddress,selected_contract)

class SpecificProjectMilestones(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/freelancer.specific-project.milestones.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        contract_check = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        
        if contract_check is None:
            return redirect(reverse("contracts:home"))
        else:
            # Get data from the POST
            target_milestone = request.POST.get("target-milestone", "0")
            
            if target_milestone != "0":
                return self.handle_standard_file_entry_request(request, **kwargs)
            
            context = self.get_context_data(request, **kwargs)
            context["errors"] = []
            return render(request, self.template_name, context)
    
    def handle_standard_file_entry_request(self,request, **kwargs):
        # Get data from the POST
        context_errors = []
        target_milestone = request.POST.get("target-milestone", "0")
        uploaded_file = request.FILES.get("deliverable", False)
        google_drive_file = request.POST.get("drive-url", "")
        google_drive_file_name = request.POST.get("drive-name", "")
        
        # Handler Class for uploading to Amazon
        amazon_handler = AmazonBotoHandler()
        
        # If we have an actual file, time to prepare it to be uploaded to AWS
        if uploaded_file != False:
            deliverable_key = uploaded_file.__str__()
            
            if self.is_this_file_extension_supported_by_inflow(deliverable_key):
                amazon_handler.standard_file_upload(request.user, target_milestone, deliverable_key, uploaded_file, kwargs.get("contract_slug"), kwargs.get("contract_id"))
            else:
                context_errors.append(("File %s is not supported at this time" % deliverable_key))
                
        elif google_drive_file != "" and google_drive_file_name != "":
            
            if self.is_this_file_extension_supported_by_inflow(google_drive_file_name):
                deliverable_key = google_drive_file_name
                amazon_handler.google_drive_file_upload(request.user, target_milestone, deliverable_key, kwargs.get("contract_slug"), kwargs.get("contract_id"), google_drive_file)
            else:
                context_errors.append(("File %s is not supported at this time" % google_drive_file_name))
                
        elif len(request.FILES) > 1:
            for dropzone_file in request.FILES:
                uploaded_file = request.FILES[dropzone_file]
                deliverable_key = uploaded_file.__str__()
                
                if self.is_this_file_extension_supported_by_inflow(deliverable_key):
                    amazon_handler.standard_file_upload(request.user, target_milestone, deliverable_key, uploaded_file, kwargs.get("contract_slug"), kwargs.get("contract_id"))
                else:
                    context_errors.append(("File %s is not supported at this time" % deliverable_key))
                    
        context = self.get_context_data(request, **kwargs)
        context["errors"] = context_errors
        return render(request, self.template_name, context)
        
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(SpecificProjectMilestones, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        contract_milestones = Milestone.objects.filter(MilestoneContract=selected_contract)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug, "number_of_revisions" : selected_contract.NumberOfAllowedRevisions }
        context["slug"] = kwargs.get("contract_slug")
        context["milestones"] = []
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
            
        # Build the necessary milestone objects for the view
        for milestone in contract_milestones:
            milestone_files = MilestoneFile.objects.filter(MilestoneForFile=milestone)
            milestone_obj = { 
                    "id" : milestone.IdMilestone, 
                    "name" : milestone.Name, 
                    "deadline_month" : milestone.Deadline.strftime("%b"), 
                    "deadline_day" : milestone.Deadline.strftime("%d"), 
                    "details" : milestone.Explanation, 
                    "amount" : "{0:.0f}".format(milestone.MilestonePaymentAmount), 
                    "state" : milestone.get_milestone_state_view(),
                    "files": [] }
            
            for file in milestone_files:
                milestone_obj["files"].append({ "id" : file.id, "name" : file.FileName, "preview_download_url" : file.FilePreviewURL })
            
            context["milestones"].append(milestone_obj)
        
        context["errors"] = []
        return context
    
    def is_this_file_extension_supported_by_inflow(self,file_name):
        extension = pathlib.Path(file_name.__str__()).suffix
        rtn_val = (extension == ".jpg" or extension == ".jpeg" or extension == ".png" or extension == ".gif" or extension == ".tiff")
        return rtn_val

class SpecificProjectOverview(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/freelancer.specific-project.overview.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        contract_check = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        
        # Base contract check so nothing gets overridden if we don't have permission
        if contract_check is None:
            return redirect(reverse("contracts:home"))
        
        # Get the Recipient that we will override
        selected_contract_recipient = Recipient.objects.filter(ContractForRecipient=contract_check).first()
        selected_contract_recipient_addresses = RecipientAddress.objects.filter(RecipientForAddress=selected_contract_recipient)
        
        # Handle Post Input
        handler = RequestInputHandler()
        contact_name = request.POST.get("contact_name", "")
        billing_name = request.POST.get("billing_name", "")
        billing_email = request.POST.get("billing_email", "")
        billing_phone = request.POST.get("billing_phone", "")
        
        selected_contract_recipient.Name = contact_name
        selected_contract_recipient.BillingName = billing_name
        selected_contract_recipient.EmailAddress = billing_email
        selected_contract_recipient.PhoneNumber = billing_phone
        selected_contract_recipient.save()
        
        for addr in selected_contract_recipient_addresses:
            addr_1_field = ("locationAddress1[%d]" % addr.id)
            addr_2_field = ("locationAddress2[%d]" % addr.id)
            addr_city_field = ("locationAddressCity[%d]" % addr.id)
            addr_state_field = ("locationAddressState[%d]" % addr.id)
            
            addr_1 = request.POST.get(addr_1_field, "")
            addr_2 = request.POST.get(addr_2_field, "")
            addr_city = request.POST.get(addr_city_field, "")
            addr_state = request.POST.get(addr_state_field, "")
            
            addr.Address1 = addr_1
            addr.Address2 = addr_2
            addr.State = addr_state
            addr.City = addr_city
            addr.save()
        
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(SpecificProjectOverview, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug, "description" : selected_contract.Description, "time_remaining" : selected_contract.calculate_time_left_string() }
        context["addresses"] = []
        
        contract_recipient = { "billing_name" : "", "billing_email" : "", "contact_name" : "", "phone_number" : "" }
        
        selected_contract_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
        
        if selected_contract_recipient is not None:
            contract_recipient["billing_name"] = selected_contract_recipient.BillingName
            contract_recipient["billing_email"] = selected_contract_recipient.EmailAddress
            contract_recipient["contact_name"] = selected_contract_recipient.Name
            context["addresses"] = RecipientAddress.objects.filter(RecipientForAddress=selected_contract_recipient)
            
            # Fracture the phone number
            if selected_contract_recipient.PhoneNumber != "" and selected_contract_recipient.PhoneNumber is not None:
                number_parts = selected_contract_recipient.PhoneNumber.split("-")
                contract_recipient["phone_number"] = selected_contract_recipient.PhoneNumber
        
        context["contract_recipient"] = contract_recipient
        return context

class SpecificProjectInvoices(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/freelancer.specific-project.invoices.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        contract_check = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        
        if contract_check is None:
            return redirect(reverse("contracts:home"))
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(SpecificProjectInvoices, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug }
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
            
        return context

class SpecificProjectFiles(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/freelancer.specific-project.files.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        contract_check = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        
        if contract_check is None:
            return redirect(reverse("contracts:home"))
        else:
            uploaded_file = request.FILES.get("deliverable", False)
            google_drive_file = request.POST.get("drive-url", "")
            google_drive_file_name = request.POST.get("drive-name", "")
            
            # Handler Class for uploading to Amazon
            amazon_handler = AmazonBotoHandler()
            
            # If we have an actual file, time to prepare it to be uploaded to AWS
            if uploaded_file != False:
                deliverable_key = uploaded_file.__str__()
                amazon_handler.standard_contract_file_upload(request.user, deliverable_key, uploaded_file, kwargs.get("contract_slug"), kwargs.get("contract_id"))
            elif google_drive_file != "" and google_drive_file_name != "":
                deliverable_key = google_drive_file_name
                amazon_handler.google_drive_contract_file_upload(request.user, deliverable_key, kwargs.get("contract_slug"), kwargs.get("contract_id"), google_drive_file)
            elif len(request.FILES) > 1:
                for dropzone_file in request.FILES:
                    uploaded_file = request.FILES[dropzone_file]
                    deliverable_key = uploaded_file.__str__()
                    amazon_handler.standard_contract_file_upload(request.user, deliverable_key, uploaded_file, kwargs.get("contract_slug"), kwargs.get("contract_id"))
                    
            context = self.get_context_data(request, **kwargs)
            return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(SpecificProjectFiles, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        selected_contract_files = ContractFile.objects.filter(ContractForFile=selected_contract)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug }
        context["contract_files"] = []
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        for file in selected_contract_files:
            context["contract_files"].append({ "id" : file.id, "name" : file.FileName, "file_size" : file.SizeOfFile, "url" : file.FileURL, "uploaded" : file.FileUploaded.strftime("%b %d %Y") })
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
            
        return context

class PreviewMilestone(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/milestone.preview.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(PreviewMilestone, self).get_context_data(**kwargs)
        
        selected_milestone = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        selected_contract = selected_milestone.MilestoneContract
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        milestone_files = MilestoneFile.objects.filter(MilestoneForFile=selected_milestone)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "slug" : selected_contract.UrlSlug }
        context["milestone_info"] = { "id" : selected_milestone.IdMilestone, "name" : selected_milestone.Name, "feedback_due" : selected_milestone.Deadline.strftime("%b %d %Y") }
        context["files"] = milestone_files
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        return context

class ScheduleSendMilestone(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/milestone.delivery.schedule.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ScheduleSendMilestone, self).get_context_data(**kwargs)
        
        selected_milestone = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        selected_contract = selected_milestone.MilestoneContract
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        milestone_files = MilestoneFile.objects.filter(MilestoneForFile=selected_milestone)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "slug" : selected_contract.UrlSlug }
        context["milestone_info"] = { "id" : selected_milestone.IdMilestone, "name" : selected_milestone.Name, "feedback_due" : selected_milestone.Deadline.strftime("%b %d %Y") }
        context["files"] = milestone_files
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        return context

class ScheduleSendMilestoneConfirm(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/milestone.delivery.schedule.confirm.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ScheduleSendMilestoneConfirm, self).get_context_data(**kwargs)
        
        selected_milestone = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        selected_contract = selected_milestone.MilestoneContract
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "slug" : selected_contract.UrlSlug }
        context["milestone_info"] = { "id" : selected_milestone.IdMilestone, "name" : selected_milestone.Name, "delivery_date" : "" }
        
        if selected_milestone.ScheduledDeliveryDate is not None:
            context["milestone_info"]["delivery_date"] = selected_milestone.ScheduledDeliveryDate.strftime("%B %d %Y")
        
        return context

class SendMilestoneNowConfirm(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/milestone.delivery.now.confirm.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(SendMilestoneNowConfirm, self).get_context_data(**kwargs)
        
        selected_milestone = self.get_contract_if_user_is_freelancer_relationship(request.user,**kwargs)
        selected_contract = selected_milestone.MilestoneContract
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "slug" : selected_contract.UrlSlug }
        context["milestone_info"] = { "id" : selected_milestone.IdMilestone, "name" : selected_milestone.Name }
        
        return context

class ClientSpecificProjectMilestones(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/client.specific-project.milestones.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ClientSpecificProjectMilestones, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_client_relationship(request.user,**kwargs)
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        contract_milestones = Milestone.objects.filter(MilestoneContract=selected_contract)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug, "number_of_revisions" : selected_contract.NumberOfAllowedRevisions }
        context["slug"] = kwargs.get("contract_slug")
        context["milestones"] = []
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
            
        # Build the necessary milestone objects for the view
        for milestone in contract_milestones:
            milestone_files = MilestoneFile.objects.filter(MilestoneForFile=milestone)
            milestone_obj = { 
                    "id" : milestone.IdMilestone, 
                    "name" : milestone.Name, 
                    "deadline_month" : milestone.Deadline.strftime("%b"), 
                    "deadline_day" : milestone.Deadline.strftime("%d"), 
                    "details" : milestone.Explanation, 
                    "amount" : "{0:.0f}".format(milestone.MilestonePaymentAmount), 
                    "state" : milestone.get_milestone_state_view(),
                    "files": [] }
            
            for file in milestone_files:
                milestone_obj["files"].append({ "id" : file.id, "name" : file.FileName, "preview_download_url" : file.FilePreviewURL })
            
            context["milestones"].append(milestone_obj)
        
        return context

class ClientSpecificProjectOverview(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/client.specific-project.overview.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ClientSpecificProjectOverview, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_client_relationship(request.user,**kwargs)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug, "description" : selected_contract.Description, "time_remaining" : selected_contract.calculate_time_left_string() }
        
        contract_recipient = { "billing_name" : "", "billing_email" : "", "contact_name" : "", "phone_number" : "" }
        
        selected_contract_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
        
        if selected_contract_recipient is not None:
            contract_recipient["billing_name"] = selected_contract_recipient.BillingName
            contract_recipient["billing_email"] = selected_contract_recipient.EmailAddress
            contract_recipient["contact_name"] = selected_contract_recipient.Name
            
            # Fracture the phone number
            if selected_contract_recipient.PhoneNumber != "" and selected_contract_recipient.PhoneNumber is not None:
                number_parts = selected_contract_recipient.PhoneNumber.split("-")
                contract_recipient["phone_number"] = selected_contract_recipient.PhoneNumber
        
        context["contract_recipient"] = contract_recipient
        return context

class ClientSpecificProjectInvoices(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/client.specific-project.invoices.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ClientSpecificProjectInvoices, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_client_relationship(request.user,**kwargs)
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug }
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
            
        return context

class ClientSpecificProjectFiles(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/client.specific-project.files.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ClientSpecificProjectFiles, self).get_context_data(**kwargs)
        
        selected_contract = self.get_contract_if_user_is_client_relationship(request.user,**kwargs)
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        selected_contract_files = ContractFile.objects.filter(ContractForFile=selected_contract)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug }
        context["contract_files"] = []
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        for file in selected_contract_files:
            context["contract_files"].append({ "id" : file.id, "name" : file.FileName, "file_size" : file.SizeOfFile, "url" : file.FileURL, "uploaded" : file.FileUploaded.strftime("%b %d %Y") })
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
            
        return context

class ClientSpecificProjectPreviewMilestone(LoginRequiredMixin, TemplateView, ContractPermissionHandler):
    template_name = "active_use/client.specific-project.milestones.preview.html"
    
    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)
        
        if not context["in_edit_mode"]:
            return redirect(reverse("contracts:home"))
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, request, **kwargs):
        # Set the context
        context = super(ClientSpecificProjectPreviewMilestone, self).get_context_data(**kwargs)
        
        # From freelancer
        selected_milestone = self.get_contract_if_user_is_client_relationship(request.user,**kwargs)
        selected_contract = selected_milestone.MilestoneContract
        selected_recipient = Recipient.objects.filter(ContractForRecipient=selected_contract).first()
        milestone_files = MilestoneFile.objects.filter(MilestoneForFile=selected_milestone)
        
        context["view_mode"] = "projects"
        context["contract_info"] = { "id" : selected_contract.id, "name" : selected_contract.Name, "state" : selected_contract.get_contract_state_view(), "total_worth" : "{0:.2f}".format(selected_contract.TotalContractWorth), "slug" : selected_contract.UrlSlug }
        context["milestone_info"] = { "id" : selected_milestone.IdMilestone, "name" : selected_milestone.Name, "feedback_due" : selected_milestone.Deadline.strftime("%b %d %Y") }
        context["contract_files"] = milestone_files
        
        if selected_recipient is None:
            context["contract_info"]["client_name"] = ""
        else:
            context["contract_info"]["client_name"] = selected_recipient.BillingName
        
        if selected_contract is None:
            context["in_edit_mode"] = False
        else:
            context["in_edit_mode"] = True
            
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

class JsonDeleteMilestoneFile(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        data = { }
        
        if "milestone_file_id" in kwargs:
            milestone_file = MilestoneFile.objects.get(id=kwargs.get("milestone_file_id"))
            
            if milestone_file.MilestoneForFile.MilestoneContract.does_this_user_have_permission_to_see_contract(request.user) is not None:
                handler = AmazonBotoHandler()
                handler.remove_file_from_user_bucket(request.user, milestone_file.MilestoneForFile.IdMilestone, milestone_file.FileName, milestone_file.MilestoneForFile.MilestoneContract.UrlSlug, milestone_file.MilestoneForFile.MilestoneContract.id)
                milestone_file.delete()
                
                data = { "success" : True, "message" : "File Found and Removed" }
            else:
                data = { "error" : True, "error-message" : "You do not have permission to access this file" }
                
        else:
            data = { "error" : True, "error-message" : "No Milestone File ID Provided" }
        
        return JsonResponse(data)

class JsonDeleteContractFile(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        data = { }
        
        if "contract_file_id" in kwargs:
            contract_file = ContractFile.objects.get(id=kwargs.get("contract_file_id"))
            
            if contract_file.ContractForFile.does_this_user_have_permission_to_see_contract(request.user) is not None:
                handler = AmazonBotoHandler()
                handler.remove_contract_file_from_user_bucket(contract_file.ContractForFile.UrlSlug, contract_file.ContractForFile.id, contract_file.FileName, request.user)
                contract_file.delete()
                
                data = { "success" : True, "message" : "File Found and Removed" }
            else:
                data = { "error" : True, "error-message" : "No Contract File ID Provided" }
        else:
            data = { "error" : True, "error-message" : "No Contract File ID Provided" }
        
        return JsonResponse(data)

class JsonScheduleMilestone(LoginRequiredMixin, View):
    def post(self, request, **kwargs):
        data = {}
        request_body = json.loads(request.body.decode('utf-8'))
        handler = RequestInputHandler()
        
        if "delivery" in request_body and "milestone_id" in kwargs:
            passed_delivery_date = handler.get_date_from_javascript(request_body["delivery"])
            selected_milestone = Milestone.objects.get(IdMilestone=kwargs.get("milestone_id"))
            
            if selected_milestone.MilestoneContract.does_this_user_have_permission_to_see_contract(request.user) is not None:
                selected_milestone.ScheduledDeliveryDate = passed_delivery_date
                selected_milestone.save()
                
                data = { "success" : True, "message" : "Milestoned scheduled for delivery" }
            else:
                data = { "error" : True, "error-message" : "Logged in user is not allowed to access this contract" }
        else:
            data = { "error" : True, "error-message" : "Delivery must be in the request body and milestone_id is required" }
        
        return JsonResponse(data)

class JsonGetContractMilestones(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        data = {}
        
        if "contract_id" in kwargs:
            contract = Contract.objects.get(id=kwargs.get("contract_id"))
            
            if contract.does_this_user_have_permission_to_see_contract(request.user) is not None:
                milestones = Milestone.objects.filter(MilestoneContract=contract)
                milestones_obj = []
                milestone_index = 1
                
                for ms in milestones:
                    milestones_obj.append({"index" : milestone_index, "id" : ms.IdMilestone, "name" : ms.Name, "description" : ms.Explanation, "payment_amount" : float(ms.MilestonePaymentAmount), "deadline" : ms.Deadline.strftime("%b %d %Y"), "estimate_hours_required" : ms.EstimateHoursRequired })
                    milestone_index = milestone_index + 1
                
                data = { "success" : True, "milestones" : milestones_obj }
            else:
                data = { "error" : True, "error-message" : "You do not have permission to view this contract", "Milestones" : [] }
        else:
            data = { "error" : True, "error-message" : "No Contract ID Provided", "Milestones" : [] }
        
        return JsonResponse(data)