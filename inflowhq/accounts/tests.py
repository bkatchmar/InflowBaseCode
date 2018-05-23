from __future__ import unicode_literals
from accounts.inflowaccountloginview import InflowLoginView
from accounts.models import NotificationSetting, UserNotificationSettings, UserSettings, UserType, UserAssociatedTypes, InFlowInvitation
from accounts.signupvalidation import ClientAccountGenerator, UserCreationBaseValidators
from contractsandprojects.models import Contract, Relationship
from django.contrib.auth.models import User
from django.test import TestCase, Client
from inflowco.models import Currency, Country
from datetime import date
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
    
    def testUsersNeedStripeFromClass(self):
        kenny = User.objects.get(username="Kenny@workinflow.co")
        clara = User.objects.get(username="Clara@workinflow.co")
        
        kenny_settings = UserSettings.objects.get(UserAccount=kenny)
        clara_settings = UserSettings.objects.get(UserAccount=clara)
        
        self.assertTrue(kenny_settings.does_this_user_need_stripe())
        self.assertFalse(clara_settings.does_this_user_need_stripe())
    
class EditNotificationsViewTests(TestCase):
    setting_string_1 = "Tips on getting the most out of InFlow"
    setting_string_2 = "The latest InFlow news and announcements"
    setting_string_3 = "Monthly newsletter featuring our best articles"
    setting_string_4 = "Account updates"
        
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
        
        if NotificationSetting.objects.filter(SettingName=self.setting_string_1).exists():
            ns1 = NotificationSetting.objects.get(SettingName=self.setting_string_1)
        else:
            ns1 = NotificationSetting.objects.create(SettingName=self.setting_string_1)
        
        if NotificationSetting.objects.filter(SettingName=self.setting_string_2).exists():
            ns2 = NotificationSetting.objects.get(SettingName=self.setting_string_2)
        else:
            ns2 = NotificationSetting.objects.create(SettingName=self.setting_string_2)
            
        if NotificationSetting.objects.filter(SettingName=self.setting_string_3).exists():
            ns3 = NotificationSetting.objects.get(SettingName=self.setting_string_3)
        else:
            ns3 = NotificationSetting.objects.create(SettingName=self.setting_string_3)
            
        if NotificationSetting.objects.filter(SettingName=self.setting_string_4).exists():
            ns4 = NotificationSetting.objects.get(SettingName=self.setting_string_4)
        else:
            ns4 = NotificationSetting.objects.create(SettingName=self.setting_string_4)
        
        # Purge the DB Entries, we're rebuild what we're expecting
        UserNotificationSettings.objects.filter(UserAccount=brian).delete()
        UserNotificationSettings.objects.filter(UserAccount=kenny).delete()
        UserNotificationSettings.objects.filter(UserAccount=clara).delete()
        
        # Brian
        UserNotificationSettings.objects.create(UserAccount=brian,Setting=ns1,Selected=True)
        UserNotificationSettings.objects.create(UserAccount=brian,Setting=ns2,Selected=True)
        UserNotificationSettings.objects.create(UserAccount=brian,Setting=ns3,Selected=True)
        UserNotificationSettings.objects.create(UserAccount=brian,Setting=ns4,Selected=True)
        
        # Kenny
        UserNotificationSettings.objects.create(UserAccount=kenny,Setting=ns1,Selected=True)
        UserNotificationSettings.objects.create(UserAccount=kenny,Setting=ns2,Selected=False)
        UserNotificationSettings.objects.create(UserAccount=kenny,Setting=ns3,Selected=False)
        UserNotificationSettings.objects.create(UserAccount=kenny,Setting=ns4,Selected=True)
        
        # Clara
        UserNotificationSettings.objects.create(UserAccount=clara,Setting=ns1,Selected=False)
        UserNotificationSettings.objects.create(UserAccount=clara,Setting=ns2,Selected=True)
        UserNotificationSettings.objects.create(UserAccount=clara,Setting=ns3,Selected=False)
        UserNotificationSettings.objects.create(UserAccount=clara,Setting=ns4,Selected=True)
        
    def test1(self):
        self.assertEqual(len(NotificationSetting.objects.all()), 4)
        
    def test2(self):
        self.assertEqual(len(NotificationSetting.objects.all()), 4)
        
    def testBrianSettings(self):
        ns1 = NotificationSetting.objects.get(SettingName=self.setting_string_1)
        ns2 = NotificationSetting.objects.get(SettingName=self.setting_string_2)
        ns3 = NotificationSetting.objects.get(SettingName=self.setting_string_3)
        ns4 = NotificationSetting.objects.get(SettingName=self.setting_string_4)
        
        c = Client()
        login_attempt = c.login(username="Brian@workinflow.co", password="Th3L10nK1ng15Fun")
        response = c.get("/account/notifications")
        
        self.assertTrue(login_attempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        
        response_context = response.context
        
        for type in response_context["settings"]:
            if type["id"] == ns1.id:
                self.assertTrue(type["selected"])
            if type["id"] == ns2.id:
                self.assertTrue(type["selected"])
            if type["id"] == ns3.id:
                self.assertTrue(type["selected"])
            if type["id"] == ns4.id:
                self.assertTrue(type["selected"])
    
    def testKennySettings(self):
        ns1 = NotificationSetting.objects.get(SettingName=self.setting_string_1)
        ns2 = NotificationSetting.objects.get(SettingName=self.setting_string_2)
        ns3 = NotificationSetting.objects.get(SettingName=self.setting_string_3)
        ns4 = NotificationSetting.objects.get(SettingName=self.setting_string_4)
        
        c = Client()
        login_attempt = c.login(username="Kenny@workinflow.co", password="Thing5Ar3Gr34t")
        response = c.get("/account/notifications")
        
        self.assertTrue(login_attempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        
        response_context = response.context
        
        for type in response_context["settings"]:
            if type["id"] == ns1.id:
                self.assertTrue(type["selected"])
            if type["id"] == ns2.id:
                self.assertFalse(type["selected"])
            if type["id"] == ns3.id:
                self.assertFalse(type["selected"])
            if type["id"] == ns4.id:
                self.assertTrue(type["selected"])
    
    def testClaraSettings(self):
        ns1 = NotificationSetting.objects.get(SettingName=self.setting_string_1)
        ns2 = NotificationSetting.objects.get(SettingName=self.setting_string_2)
        ns3 = NotificationSetting.objects.get(SettingName=self.setting_string_3)
        ns4 = NotificationSetting.objects.get(SettingName=self.setting_string_4)
        
        c = Client()
        login_attempt = c.login(username="Clara@workinflow.co", password="Thing5Ar3Gr34t")
        response = c.get("/account/notifications")
        
        self.assertTrue(login_attempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        
        response_context = response.context
        
        for type in response_context["settings"]:
            if type["id"] == ns1.id:
                self.assertFalse(type["selected"])
            if type["id"] == ns2.id:
                self.assertTrue(type["selected"])
            if type["id"] == ns3.id:
                self.assertFalse(type["selected"])
            if type["id"] == ns4.id:
                self.assertTrue(type["selected"])

class UserGeneratedSlugTests(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        # Users
        user_1 = User.objects.create(username="User1@workinflow.co",email="User1@workinflow.co",first_name="Brian",last_name="Katchmar")
        user_1.set_password("Th3L10nK1ng15Fun")
        user_1.save()
        settings_user_1 = UserSettings()
        settings_user_1 = settings_user_1.get_settings_based_on_user(user_1)
        settings_user_1.BusinessName = "MIAC"
        settings_user_1.Region = "New York"
        settings_user_1.save()
        
        user_2 = User.objects.create(username="User2@workinflow.co",email="User2@workinflow.co",first_name="Brian",last_name="Katchmar")
        user_2.set_password("Thing5Ar3Gr34t")
        user_2.save()
        settings_user_2 = UserSettings()
        settings_user_2 = settings_user_2.get_settings_based_on_user(user_2)
        settings_user_2.save()
        
        user_3 = User.objects.create(username="User3@workinflow.co",email="User3@workinflow.co",first_name="Brian",last_name="Katchmar")
        user_3.set_password("Thing5Ar3Gr34t")
        user_3.save()
        settings_user_3 = UserSettings()
        settings_user_3 = settings_user_3.get_settings_based_on_user(user_3)
        settings_user_3.BusinessName = "InFlow"
        settings_user_3.Region = "New York"
        settings_user_3.PhoneNumber = "2125555555"
        settings_user_3.StripeConnectAccountKey = "1234567890"
        settings_user_3.save()
        
    def testUniqueUserSlugsGeneratedEvenIfMultipleUsersAlreadyExists(self):
        user_1 = User.objects.get(username="User1@workinflow.co")
        settings_user_1 = UserSettings()
        settings_user_1 = settings_user_1.get_settings_based_on_user(user_1)
        
        user_2 = User.objects.get(username="User2@workinflow.co")
        settings_user_2 = UserSettings()
        settings_user_2 = settings_user_2.get_settings_based_on_user(user_2)
        
        user_3 = User.objects.get(username="User3@workinflow.co")
        settings_user_3 = UserSettings()
        settings_user_3 = settings_user_1.get_settings_based_on_user(user_3)
        
        self.assertIsNotNone(settings_user_1.UrlSlug)
        self.assertIsNotNone(settings_user_2.UrlSlug)
        self.assertIsNotNone(settings_user_3.UrlSlug)
        
        self.assertNotEqual(settings_user_1.UrlSlug, settings_user_2.UrlSlug)
        self.assertNotEqual(settings_user_1.UrlSlug, settings_user_3.UrlSlug)
        self.assertNotEqual(settings_user_2.UrlSlug, settings_user_3.UrlSlug)

class ClientAccountGeneratorTests(TestCase):
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        # Users
        brian_1 = User.objects.create(username="Brian@workinflow.co",email="Brian@workinflow.co",first_name="Brian",last_name="Katchmar")
        brian_1.set_password("Th3L10nK1ng15Fun")
        brian_1.save()
        
        brian_2 = User.objects.create(username="VideoXPG@gmail.com",email="VideoXPG@gmail.com",first_name="Brian",last_name="Katchmar")
        brian_2.set_password("Th3L10nK1ng15Fun")
        brian_2.save()
    
    def testAllGuidElementsAreUnique(self):
        generator = ClientAccountGenerator()
        
        guid_1 = generator.generate_guid()
        guid_2 = generator.generate_guid()
        guid_3 = generator.generate_guid()
        
        self.assertNotEqual(guid_1, guid_2)
        self.assertNotEqual(guid_1, guid_3)
        self.assertNotEqual(guid_2, guid_3)
    
    def testInvitationLinkExpiry(self):
        july_30 = date(2018,7,30)
        august_20 = date(2018,8,20)
        far_out = date(2030,1,1)
        
        generator = ClientAccountGenerator()
        
        new_user_1 = User.objects.create(username="User1@workinflow.co",email="User1@workinflow.co")
        new_user_2 = User.objects.create(username="User2@workinflow.co",email="User2@workinflow.co")
        new_user_3 = User.objects.create(username="User3@workinflow.co",email="User3@workinflow.co")
        
        i1 = InFlowInvitation.objects.create(InvitedUser=new_user_1,GUID=generator.generate_guid(),Expiry=july_30)
        i2 = InFlowInvitation.objects.create(InvitedUser=new_user_2,GUID=generator.generate_guid(),Expiry=august_20)
        i3 = InFlowInvitation.objects.create(InvitedUser=new_user_3,GUID=generator.generate_guid(),Expiry=far_out)
        
        self.assertTrue(august_20 > july_30) # August 20 is after July 30
        self.assertFalse(i1.has_this_invitation_expired(date(2018,7,25))) # Expect this to pass as July 25th is still before July 30th
        self.assertTrue(i1.has_this_invitation_expired(august_20)) # Expect this to fail as August 20th is well past July 30th
        self.assertFalse(i3.has_this_invitation_expired()) # Will fail once the current date is January 1st, 2030....we have time
        
    def testAccountCheck(self):
        generator = ClientAccountGenerator()
        
        self.assertTrue(generator.does_this_account_already_exists("brian@workinflow.co"))
        self.assertTrue(generator.does_this_account_already_exists("videoxpg@gmail.com"))
        self.assertFalse(generator.does_this_account_already_exists("bkatchmar@gmail.com"))
        
    def testInvitationCreation(self):
        generator = ClientAccountGenerator()
        
        number_of_invitations_1 = len(InFlowInvitation.objects.all())
        
        generator.create_invitation("bkatchmar@gmail.com")
        
        number_of_invitations_2 = len(InFlowInvitation.objects.all())
        
        self.assertNotEqual(number_of_invitations_1, number_of_invitations_2)
        
        new_user = User.objects.get(email="bkatchmar@gmail.com")
        new_user_invitation = InFlowInvitation.objects.get(InvitedUser=new_user)
        
        self.assertNotEqual(date.today(), new_user_invitation.Expiry)
    
    def testExpirationFromInvitationView(self):
        january_1 = date(2017,1,1)
        far_out = date(2030,1,1)
        
        generator = ClientAccountGenerator()
        
        new_user_1 = User.objects.create(username="User1@workinflow.co",email="User1@workinflow.co")
        new_user_2 = User.objects.create(username="User2@workinflow.co",email="User2@workinflow.co")
        
        i1 = InFlowInvitation.objects.create(InvitedUser=new_user_1,GUID=generator.generate_guid(),Expiry=january_1)
        i2 = InFlowInvitation.objects.create(InvitedUser=new_user_2,GUID=generator.generate_guid(),Expiry=far_out)
        
        c = Client()
        
        response = c.get(("/account/invitation/%s" % i1.GUID))
        self.assertEqual(200,response.status_code)
        self.assertTrue(response.context["is_expired"])
        
        response = c.get(("/account/invitation/%s" % i2.GUID))
        self.assertEqual(200,response.status_code)
        self.assertFalse(response.context["is_expired"])

class ClientContractRelationshipTests(TestCase):
    contract_name_1 = "ClientContractRelationshipTests Contract 1"
    
    def setUp(self):
        # Necessary Currency Objects
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        # Users
        brian_1 = User.objects.create(username="Brian@workinflow.co",email="Brian@workinflow.co",first_name="Brian",last_name="Katchmar")
        brian_1.set_password("Th3L10nK1ng15Fun")
        brian_1.save()
        
        settings_brian_1 = UserSettings()
        settings_brian_1 = settings_brian_1.get_settings_based_on_user(brian_1)
        settings_brian_1.save()
        
        brian_2 = User.objects.create(username="VideoXPG@gmail.com",email="VideoXPG@gmail.com",first_name="Brian",last_name="Katchmar")
        brian_2.set_password("Th3L10nK1ng15Fun")
        brian_2.save()
        
        settings_brian_2 = UserSettings()
        settings_brian_2 = settings_brian_2.get_settings_based_on_user(brian_2)
        settings_brian_2.save()
        
        if not Contract.objects.filter(Name=self.contract_name_1).exists():
            contract_1 = Contract.objects.create(Creator=brian_1,Name=self.contract_name_1,StartDate=date.today(),EndDate=date.today())
            Relationship.objects.create(ContractUser=brian_1,ContractForRelationship=contract_1,RelationshipType="f")
            Relationship.objects.create(ContractUser=brian_2,ContractForRelationship=contract_1,RelationshipType="c")
    
    def testRelationshipGenerator(self):
        new_email_address = "ClientContractRelationshipTestsUser1@workinflow.co"
        generator = ClientAccountGenerator()
        
        brian_1 = User.objects.get(username="Brian@workinflow.co")
        contract_1 = Contract.objects.get(Name=self.contract_name_1)
        
        self.assertEqual(len(Relationship.objects.filter(ContractForRelationship=contract_1)), 2)
        
        generator.create_relationship_for_contract(new_email_address,contract_1)
        
        self.assertEqual(len(Relationship.objects.filter(ContractForRelationship=contract_1)), 3)
    
    def testDoesUserNeedStripeIfTheyHaveClientRelationship(self):
        brian_2 = User.objects.get(username="VideoXPG@gmail.com")
        settings = UserSettings.objects.get(UserAccount=brian_2)
        self.assertFalse(settings.does_this_user_need_stripe())