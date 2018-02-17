from __future__ import unicode_literals
from accounts.models import UserSettings
from accounts.signupvalidation import UserCreationBaseValidators
from django.contrib.auth.models import User
from django.test import TestCase, Client
from inflowco.models import Country, Currency
import pytz

class BaseUserTestCase(TestCase):
    def setUp(self):
        User.objects.create(
                            username="brian",
                            email="brian@workinflow.co",
                            password="ilikechickenfingersandpizza",
                            first_name="Brian",
                            last_name="Katchmar",
                            is_staff=True,
                            is_active=True,
                            is_superuser=True)

    def test_did_user_get_created(self):
        superuser = User.objects.get(username="brian")
        self.assertEqual(superuser.first_name, "Brian")
        
class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        testUser = User.objects.create(
                            username="brian",
                            email="brian@workinflow.co",
                            first_name="Brian",
                            last_name="Katchmar",
                            is_staff=True,
                            is_active=True,
                            is_superuser=True)
        
        testUser.set_password("ilikechickenfingersandpizza")
        testUser.save()
    
    def test_not_logged_in_user_get_kicked_out(self):
        c = Client()
        response = c.get('/inflow/account/')
        self.assertEqual(302,response.status_code)
        
    def test_does_user_see_page_when_logged_in(self):
        c = Client()
        loginAttempt = c.login(username='brian', password='ilikechickenfingersandpizza')
        response = c.get('/inflow/account/')
        
        self.assertTrue(loginAttempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        
    def test_does_user_see_expected_information(self):
        c = Client()
        loginAttempt = c.login(username='brian', password='ilikechickenfingersandpizza')
        response = c.get('/inflow/account/')
        
        self.assertEqual(response.context["settings"].UserAccount.username, "brian")
        self.assertEqual(response.context["settings"].UserAccount.first_name, "Brian")
        self.assertEqual(response.context["settings"].UserAccount.last_name, "Katchmar")

class SignUpValidationTests(TestCase):
    def setUp(self):
        User.objects.create(
            username="brian",
            email="brian@workinflow.co",
            password="ilikechickenfingersandpizza",
            first_name="Brian",
            last_name="Katchmar",
            is_staff=True,
            is_active=True,
            is_superuser=True)
        
    def test_validation(self):
        validator = UserCreationBaseValidators()
        validator.attempt_to_create_user("","","arandompassword",True)
        self.assertEqual(validator.error_thrown, False)
        
        validator1 = UserCreationBaseValidators()
        validator1.attempt_to_create_user("useremail@email.com","Brian","Apple",False)
        self.assertEqual(validator1.error_thrown, False)