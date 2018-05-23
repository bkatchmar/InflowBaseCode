from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import PermissionDenied
from contractsandprojects.models import Contract, Milestone

class ContractPermissionHandler():
    def get_contract_if_user_is_creator(self,user,**kwargs):
        contract_return_val = None
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if "milestone_id" in kwargs:
            milestone_return_val = Milestone.objects.filter(IdMilestone=kwargs.get("milestone_id")).first()
            
            if milestone_return_val is None:
                raise Http404()
            elif not milestone_return_val.MilestoneContract.is_the_user_the_creator_of_contract(user):
                raise PermissionDenied() # Raise 403
            elif int(milestone_return_val.MilestoneContract.id) != int(kwargs.get("contract_id")):
                raise ValueError(("Milestone (%s) to Contract (%s) Mismatch" % (kwargs.get("milestone_id"), kwargs.get("contract_id"))))
            
            return milestone_return_val
        
        elif "contract_slug" in kwargs and "contract_id" in kwargs:
            contract_return_val = Contract.objects.filter(id=kwargs.get("contract_id"),UrlSlug=kwargs.get("contract_slug")).first()
            
            if contract_return_val is None: # Just exit and raise a 404 message
                raise Http404()
            elif not contract_return_val.is_the_user_the_creator_of_contract(user):
                raise PermissionDenied() # Raise 403
            
        elif "contract_id" in kwargs:
            contract_return_val = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            
            if contract_return_val is None: # Just exit and raise a 404 message
                raise Http404()
            elif not contract_return_val.is_the_user_the_creator_of_contract(user):
                raise PermissionDenied() # Raise 403
        
        return contract_return_val
        
    def get_contract_if_user_has_relationship(self,user,**kwargs):
        contract_return_val = None
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if "milestone_id" in kwargs:
            milestone_return_val = Milestone.objects.filter(IdMilestone=kwargs.get("milestone_id")).first()
            
            if milestone_return_val is None:
                raise Http404()
            elif not milestone_return_val.MilestoneContract.does_this_user_have_permission_to_see_contract(user):
                raise PermissionDenied() # Raise 403
            elif int(milestone_return_val.MilestoneContract.id) != int(kwargs.get("contract_id")):
                raise ValueError(("Milestone (%s) to Contract (%s) Mismatch" % (kwargs.get("milestone_id"), kwargs.get("contract_id"))))
            
            return milestone_return_val
            
        elif "contract_slug" in kwargs and "contract_id" in kwargs:
            contract_return_val = Contract.objects.filter(id=kwargs.get("contract_id"),UrlSlug=kwargs.get("contract_slug")).first()
            
            if contract_return_val is None: # Just exit and raise a 404 message
                raise Http404()
            elif not contract_return_val.does_this_user_have_permission_to_see_contract(user):
                raise PermissionDenied() # Raise 403
            
        elif "contract_id" in kwargs:
            contract_return_val = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            
            if contract_return_val is None: # Just exit and raise a 404 message
                raise Http404()
            elif not contract_return_val.does_this_user_have_permission_to_see_contract(user):
                raise PermissionDenied() # Raise 403
        
        return contract_return_val
    
    def get_contract_if_user_is_freelancer_relationship(self,user,**kwargs):
        contract_return_val = None
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if "milestone_id" in kwargs:
            milestone_return_val = Milestone.objects.filter(IdMilestone=kwargs.get("milestone_id")).first()
            
            if milestone_return_val is None:
                raise Http404()
            elif not milestone_return_val.MilestoneContract.is_the_user_a_freelancer(user):
                raise PermissionDenied() # Raise 403
            elif int(milestone_return_val.MilestoneContract.id) != int(kwargs.get("contract_id")):
                raise ValueError(("Milestone (%s) to Contract (%s) Mismatch" % (kwargs.get("milestone_id"), kwargs.get("contract_id"))))
            
            return milestone_return_val
            
        elif "contract_slug" in kwargs and "contract_id" in kwargs:
            contract_return_val = Contract.objects.filter(id=kwargs.get("contract_id"),UrlSlug=kwargs.get("contract_slug")).first()
            
            if contract_return_val is None: # Just exit and raise a 404 message
                raise Http404()
            elif not contract_return_val.is_the_user_a_freelancer(user):
                raise PermissionDenied() # Raise 403
            
        elif "contract_id" in kwargs:
            contract_return_val = Contract.objects.filter(id=kwargs.get("contract_id")).first()
            
            if contract_return_val is None: # Just exit and raise a 404 message
                raise Http404()
            elif not contract_return_val.is_the_user_a_freelancer(user):
                raise PermissionDenied() # Raise 403
        
        return contract_return_val