from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import PermissionDenied
from contractsandprojects.models import Contract

class ContractPermissionHandler():
    def get_contract_if_user_has_relationship(self,user,**kwargs):
        contract_return_val = None
        
        # If we even passed a variable in, go ahead and check to make sure its an actual contract
        if "contract_slug" in kwargs and "contract_id" in kwargs:
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