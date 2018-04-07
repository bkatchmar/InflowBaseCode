from __future__ import unicode_literals
from accounts.inflowaccountloginview import InflowLoginView
from accounts.models import NotificationSetting, UserSettings, UserType, UserAssociatedTypes
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
        kenny.set_password("Thing5Ar3Gr34t")
        kenny.save()
        settings_kenny = UserSettings()
        settings_kenny = settings_brian.get_settings_based_on_user(kenny)
        settings_kenny.save()
        UserAssociatedTypes.objects.create(UserAccount=kenny,UserFreelanceType=u2)
        UserAssociatedTypes.objects.create(UserAccount=kenny,UserFreelanceType=u3)
        
        clara = User.objects.create(username="clara",email="Clara@workinflow.co",first_name="Clara",last_name="Chang") # Has User Settings, no associated types
        clara.set_password("Thing5Ar3Gr34t")
        clara.save()
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
        
class UserOnBoardingScreen1TestKenny(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        # Types
        u1 = UserType.objects.create(Name="Kenny Type 1")
        u2 = UserType.objects.create(Name="Kenny Type 2")
        u3 = UserType.objects.create(Name="Kenny Type 3")
        
        kenny = User.objects.create(username="kenny",email="Kenny@workinflow.co",first_name="Kenny",last_name="Kim") # Has User Settings, has associated types, neither of the two fields we check
        kenny.set_password("Thing5Ar3Gr34t")
        kenny.save()
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        settings_kenny.save()
        UserAssociatedTypes.objects.create(UserAccount=kenny,UserFreelanceType=u2)
        UserAssociatedTypes.objects.create(UserAccount=kenny,UserFreelanceType=u3)
        
    def test_onboarding_screen1_context_kenny(self):
        c = Client()
        loginAttempt = c.login(username='kenny', password='Thing5Ar3Gr34t')
        response = c.get('/account/create/onboarding-1')
        
        self.assertTrue(loginAttempt) # User was able to log in
        
        user_types = response.context["user_types"]
        for type in user_types:
            if type.Name == "Kenny Type 2" or type.Name == "Kenny Type 3":
                self.assertTrue(type.Selected)
        
        self.assertGreater(len(user_types), 0)
        
class UserOnBoardingScreen1TestClara(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        # Types
        u1 = UserType.objects.create(Name="Clara Type 1")
        u2 = UserType.objects.create(Name="Clara Type 2")
        u3 = UserType.objects.create(Name="Clara Type 3")
        
        clara = User.objects.create(username="clara",email="Clara@workinflow.co",first_name="Clara",last_name="Chang") # Has User Settings, no associated types
        clara.set_password("Thing5Ar3Gr34t")
        clara.save()
        settings_clara = UserSettings()
        settings_clara = settings_clara.get_settings_based_on_user(clara)
        settings_clara.BusinessName = "InFlow"
        settings_clara.Region = "New York"
        settings_clara.save()
    
    def test_onboarding_screen1_context_clara(self):
        c = Client()
        loginAttempt = c.login(username='clara', password='Thing5Ar3Gr34t')
        response = c.get('/account/create/onboarding-1')
        
        self.assertTrue(loginAttempt) # User was able to log in
        
        user_types = response.context["user_types"]
        for type in user_types:
            self.assertFalse(type.Selected)
        
        self.assertGreater(len(user_types), 0)

class EditProfileViewTests(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        kenny = User.objects.create(username="Kenny@workinflow.co",email="Kenny@workinflow.co",first_name="Kenny",last_name="Kim")
        kenny.set_password("Thing5Ar3Gr34t")
        kenny.save()
        
        clara = User.objects.create(username="Clara@workinflow.co",email="Clara@workinflow.co",first_name="Clara",last_name="Chang")
        clara.set_password("Thing5Ar3Gr34t")
        clara.save()
        
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        settings_kenny.save()
        
        settings_clara = UserSettings()
        settings_clara = settings_clara.get_settings_based_on_user(clara)
        settings_clara.BusinessName = "InFlow"
        settings_clara.Region = "New York"
        settings_clara.PhoneNumber = "2125555555"
        settings_clara.save()
        
    def testKennyGet(self):
        kenny = User.objects.get(username="Kenny@workinflow.co")
        clara = User.objects.get(username="Clara@workinflow.co")
        
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        
        settings_clara = UserSettings()
        settings_clara = settings_clara.get_settings_based_on_user(clara)
        
        c = Client()
        loginAttempt = c.login(username='Kenny@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.get("/account/settings")
        
        self.assertEqual(response.context["first_name"], kenny.first_name)
        self.assertEqual(response.context["last_name"], kenny.last_name)
        self.assertEqual(response.context["email"], kenny.email)
        self.assertEqual(response.context["phone_number"], "")
        
        self.assertNotEqual(response.context["first_name"], clara.first_name)
        self.assertNotEqual(response.context["last_name"], clara.last_name)
        self.assertNotEqual(response.context["email"], clara.email)
        self.assertNotEqual(response.context["phone_number"], settings_clara.PhoneNumber)
    
    def testClaraGet(self):
        kenny = User.objects.get(username="Kenny@workinflow.co")
        clara = User.objects.get(username="Clara@workinflow.co")
        
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        
        settings_clara = UserSettings()
        settings_clara = settings_clara.get_settings_based_on_user(clara)
        
        c = Client()
        loginAttempt = c.login(username='Clara@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.get("/account/settings")
        
        self.assertNotEqual(response.context["first_name"], kenny.first_name)
        self.assertNotEqual(response.context["last_name"], kenny.last_name)
        self.assertNotEqual(response.context["email"], kenny.email)
        self.assertNotEqual(response.context["phone_number"], "")
        
        self.assertEqual(response.context["first_name"], clara.first_name)
        self.assertEqual(response.context["last_name"], clara.last_name)
        self.assertEqual(response.context["email"], clara.email)
        self.assertEqual(response.context["phone_number"], settings_clara.PhoneNumber)
        
    def testKennyPostBasicInfoEdit(self):
        kenny = User.objects.get(username="Kenny@workinflow.co")
        
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        
        c = Client()
        loginAttempt = c.login(username='Kenny@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.post('/account/settings', {'first-name' : 'Snickity', 'last-name' : 'Snack', 'email-address' : 'Kenny@workinflow.co', 'phone-number' : '2121234567'})
        
        self.assertEqual(response.context["first_name"], "Snickity")
        self.assertEqual(response.context["last_name"], "Snack")
        
        self.assertNotEqual(response.context["first_name"], "Kenny")
        self.assertNotEqual(response.context["last_name"], "Kim")
        
        self.assertTrue("error_message" not in response.context)
        
    def testKennyPostTryToChangeToClara(self):
        kenny = User.objects.get(username="Kenny@workinflow.co")
        
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        
        c = Client()
        loginAttempt = c.login(username='Kenny@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.post('/account/settings', {'first-name' : 'Snickity', 'last-name' : 'Snack', 'email-address' : 'Clara@workinflow.co', 'phone-number' : '2121234567'})
        
        self.assertTrue("error_message" in response.context)
    
class EditAccountViewTests(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        kenny = User.objects.create(username="Kenny@workinflow.co",email="Kenny@workinflow.co",first_name="Kenny",last_name="Kim")
        kenny.set_password("Thing5Ar3Gr34t")
        kenny.save()
        
        clara = User.objects.create(username="Clara@workinflow.co",email="Clara@workinflow.co",first_name="Clara",last_name="Chang")
        clara.set_password("Thing5Ar3Gr34t")
        clara.save()
        
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        settings_kenny.save()
        
        settings_clara = UserSettings()
        settings_clara = settings_clara.get_settings_based_on_user(clara)
        settings_clara.BusinessName = "InFlow"
        settings_clara.Region = "New York"
        settings_clara.PhoneNumber = "2125555555"
        settings_clara.StripeConnectAccountKey = "1234567890"
        settings_clara.save()
        
    def testKennyNeedsStripe(self):
        c = Client()
        loginAttempt = c.login(username='Kenny@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.get('/account/edit-account')
        
        self.assertTrue(response.context["needs_stripe"])
        
    def testClaraNeedsStripe(self):
        c = Client()
        loginAttempt = c.login(username='Clara@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.get('/account/edit-account')
        
        self.assertFalse(response.context["needs_stripe"])
    
class EditNotificationsViewTests(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        # Users
        brian = User.objects.create(username="Brian@workinflow.co",email="Brian@workinflow.co",first_name="Brian",last_name="Katchmar")
        brian.set_password("Th3L10nK1ng15Fun")
        brian.save()
        settings_brian = UserSettings()
        settings_brian = settings_brian.get_settings_based_on_user(brian)
        settings_brian.BusinessName = "MIAC"
        settings_brian.Region = "New York"
        settings_brian.save()
        
        kenny = User.objects.create(username="Kenny@workinflow.co",email="Kenny@workinflow.co",first_name="Kenny",last_name="Kim") # Has User Settings, has associated types, neither of the two fields we check
        kenny.set_password("Thing5Ar3Gr34t")
        kenny.save()
        settings_kenny = UserSettings()
        settings_kenny = settings_kenny.get_settings_based_on_user(kenny)
        settings_kenny.save()
        
        clara = User.objects.create(username="Clara@workinflow.co",email="Clara@workinflow.co",first_name="Clara",last_name="Chang")
        clara.set_password("Thing5Ar3Gr34t")
        clara.save()
        settings_clara = UserSettings()
        settings_clara = settings_clara.get_settings_based_on_user(clara)
        settings_clara.BusinessName = "InFlow"
        settings_clara.Region = "New York"
        settings_clara.PhoneNumber = "2125555555"
        settings_clara.StripeConnectAccountKey = "1234567890"
        settings_clara.save()
        
        # Notification Settings
        setting_string_1 = "Tips on getting the most out of InFlow"
        setting_string_2 = "The latest InFlow news and announcements"
        setting_string_3 = "Monthly newsletter featuring our best articles"
        setting_string_4 = "Account updates"
        
        if NotificationSetting.objects.filter(SettingName=setting_string_1).exists():
            ns1 = NotificationSetting.objects.get(SettingName=setting_string_1)
        else:
            ns1 = NotificationSetting.objects.create(SettingName=setting_string_1)
        
        if NotificationSetting.objects.filter(SettingName=setting_string_2).exists():
            ns2 = NotificationSetting.objects.get(SettingName=setting_string_2)
        else:
            ns2 = NotificationSetting.objects.create(SettingName=setting_string_2)
            
        if NotificationSetting.objects.filter(SettingName=setting_string_3).exists():
            ns3 = NotificationSetting.objects.get(SettingName=setting_string_3)
        else:
            ns3 = NotificationSetting.objects.create(SettingName=setting_string_3)
            
        if NotificationSetting.objects.filter(SettingName=setting_string_4).exists():
            ns4 = NotificationSetting.objects.get(SettingName=setting_string_4)
        else:
            ns4 = NotificationSetting.objects.create(SettingName=setting_string_4)
            
    def test1(self):
        self.assertEqual(len(NotificationSetting.objects.all()), 4)
        
    def test2(self):
        self.assertEqual(len(NotificationSetting.objects.all()), 4)