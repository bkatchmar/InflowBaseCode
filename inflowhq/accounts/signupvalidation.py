from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserCreationBaseValidators:
    error_message = ""
    error_thrown = False
    created_user = None
    
    def __init__(self):
        self.error_message = ""
        self.error_thrown = False
        self.created_user = None
    
    def attempt_to_create_user(self,username,name,password,agreed):
        if not agreed:
            self.error_thrown = True
            self.error_message = "You must agree to the terms of service in order to proceed"
        elif username == "" and name == "" and password == "":
            self.error_thrown = True
            self.error_message = "All fields are required"
        
        # Check if we already have a user by that email
        self.created_user = User.objects.filter(email=username).first()
        if not self.created_user is None:
            self.error_thrown = True
            self.error_message = "A username with that email already exists"
            
        if not self.error_thrown:
            # Go ahead and try to validate the password
            # Create the user as well, but keep it inactive until we are ready to validate
            self.created_user = User.objects.create(username=username,email=username,first_name=name,is_staff=False,is_active=False,is_superuser=False)
            
            try:
                validate_password(password, user=self.created_user)
                self.created_user.is_active = True
                self.created_user.set_password(password)
                self.created_user.save()
            except ValidationError as val:
                self.error_thrown = True
                self.error_message = val.__str__()
                self.created_user.delete()