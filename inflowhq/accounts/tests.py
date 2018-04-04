from __future__ import unicode_literals
from accounts.inflowaccountloginview import InflowLoginView
from accounts.models import UserSettings, UserType, UserAssociatedTypes
from accounts.signupvalidation import UserCreationBaseValidators
from django.contrib.auth.models import User
from django.test import TestCase, Client
from inflowco.models import Currency, Country
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
        response = c.get('/inflow')
        self.assertEqual(301,response.status_code)
        
    def test_does_user_see_page_when_logged_in(self):
        c = Client()
        loginAttempt = c.login(username='brian', password='ilikechickenfingersandpizza')
        response = c.get('/inflow/')
        
        self.assertTrue(loginAttempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        
    def test_does_user_see_expected_information(self):
        c = Client()
        loginAttempt = c.login(username='brian', password='ilikechickenfingersandpizza')
        response = c.get('/account/settings')
        
        self.assertEqual(response.context["first_name"], "Brian")
        self.assertEqual(response.context["last_name"], "Katchmar")
        self.assertEqual(response.context["email"], "brian@workinflow.co")
        self.assertEqual(response.context["phone_number"], "")

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
        self.assertEqual(validator.error_thrown, True)
        
        validator1 = UserCreationBaseValidators()
        validator1.attempt_to_create_user("useremail@email.com","Brian","Apple",False)
        self.assertEqual(validator1.error_thrown, True)
        
        validator2 = UserCreationBaseValidators()
        validator2.attempt_to_create_user("useremail@email.com","Brian","Brian",False)
        self.assertEqual(validator2.error_thrown, True)
        
        validator3 = UserCreationBaseValidators()
        validator3.attempt_to_create_user("VideoXPG@gmail.com","Brian","Th3l10nk1ng",True)
        self.assertEqual(validator3.error_thrown, False)
        
        validator4 = UserCreationBaseValidators()
        validator4.attempt_to_create_user("VideoXPG@gmail.com","Brian","Th3l10nk1ng",False)
        self.assertEqual(validator4.error_thrown, True)
        
class UserNeedsOnBoardingTest(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        # Types
        u1 = UserType.objects.create(Name="Type 1")
        u2 = UserType.objects.create(Name="Type 2")
        u3 = UserType.objects.create(Name="Type 3")
        
        brian = User.objects.create(username="brian",email="brian@workinflow.co",first_name="Brian",last_name="Katchmar") # Passes
        settings_brian = UserSettings()
        settings_brian = settings_brian.get_settings_based_on_user(brian)
        settings_brian.BusinessName = "MIAC"
        settings_brian.Region = "New York"
        settings_brian.save()
        UserAssociatedTypes.objects.create(UserAccount=brian,UserFreelanceType=u1)
        
        josh = User.objects.create(username="josh",email="josh@workinflow.co",first_name="Josh",last_name="Blank") # No User Settings
        
        kenny = User.objects.create(username="kenny",email="Kenny@workinflow.co",first_name="Kenny",last_name="Kim") # Has User Settings, has associated types, neither of the two fields we check
        settings_kenny = UserSettings()
        settings_kenny = settings_brian.get_settings_based_on_user(kenny)
        settings_kenny.save()
        UserAssociatedTypes.objects.create(UserAccount=kenny,UserFreelanceType=u2)
        UserAssociatedTypes.objects.create(UserAccount=kenny,UserFreelanceType=u3)
        
        clara = User.objects.create(username="clara",email="Clara@workinflow.co",first_name="Clara",last_name="Chang") # Has User Settings, no associated types
        settings_clara = UserSettings()
        settings_clara = settings_brian.get_settings_based_on_user(clara)
        settings_clara.BusinessName = "InFlow"
        settings_clara.Region = "New York"
        settings_clara.save()
    
    def test_needs_onboarding(self):
        login_view = InflowLoginView()
        brian = User.objects.get(username="brian")
        self.assertEqual(login_view.determine_if_user_needs_onboarding(brian), False)
        
        josh = User.objects.get(username="josh")
        self.assertEqual(login_view.determine_if_user_needs_onboarding(josh), True)
        
        kenny = User.objects.get(username="kenny")
        self.assertEqual(login_view.determine_if_user_needs_onboarding(kenny), True)
        
        clara = User.objects.get(username="clara")
        self.assertEqual(login_view.determine_if_user_needs_onboarding(clara), True)