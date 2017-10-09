from __future__ import unicode_literals
from accounts.models import UserSettings, UserPaymentHistory
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone
from inflowco.models import Currency
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
        
class UserPaymentHistoryTestCase(TestCase):
    def setUp(self):
        usd = Currency.objects.create()
    
        firstUser = User.objects.create(username="brian",
                                        email="brian@workinflow.co",
                                        password="ilikechickenfingersandpizza",
                                        first_name="Brian",
                                        last_name="Katchmar",
                                        is_staff=True,
                                        is_active=True,
                                        is_superuser=True)
        secondUser = User.objects.create(username="brian2",
                                        email="brian2@workinflow.co",
                                        password="ilikechickenfingersandpizza",
                                        first_name="Brian",
                                        last_name="Katchmar",
                                        is_staff=True,
                                        is_active=True,
                                        is_superuser=True)
        
        thirdUser = User.objects.create(username="brian3",
                                        email="brian3@workinflow.co",
                                        password="ilikechickenfingersandpizza",
                                        first_name="Brian",
                                        last_name="Katchmar",
                                        is_staff=True,
                                        is_active=True,
                                        is_superuser=True)
        
        # Time Zone Setting
        timezone.activate(pytz.timezone("America/New_York"))
        
        # Get Settings
        date_first = date(2017,9,20)
        time_first = time(12, 0, 0, tzinfo=timezone.get_current_timezone())
        aware_datetime_first = datetime.combine(date_first, time_first)
        UserSettings.objects.create(UserAccount=firstUser,
                                    Active=True,
                                    Joined=aware_datetime_first,
                                    BaseCurrency=usd,
                                    PaymentLevel='s')
        
        date_second = date(2017,9,21)
        time_second = time(12, 0, 0, tzinfo=timezone.get_current_timezone())
        aware_datetime_second = datetime.combine(date_second, time_second)
        UserSettings.objects.create(UserAccount=secondUser,
                                    Active=True,
                                    Joined=aware_datetime_second,
                                    BaseCurrency=usd,
                                    PaymentLevel='s')
        
        date_third = date(2017,9,21)
        time_third = time(12, 0, 0, tzinfo=timezone.get_current_timezone())
        aware_datetime_third = datetime.combine(date_third, time_third)
        UserSettings.objects.create(UserAccount=thirdUser,
                                    Active=False,
                                    Joined=aware_datetime_third,
                                    BaseCurrency=usd,
                                    PaymentLevel='s')
        
        # First User Payments
        UserPaymentHistory.objects.create(UserAccount=firstUser,
                                          DateCharged=date(2017,9,20),
                                          NextBillingDate=date(2017,9,20)+relativedelta(days=+1),
                                          PaymentLevel='s')
        UserPaymentHistory.objects.create(UserAccount=firstUser,
                                          DateCharged=date(2017,9,21),
                                          NextBillingDate=date(2017,9,21)+relativedelta(days=+1),
                                          PaymentLevel='s')
        
        # Second User Payments
        UserPaymentHistory.objects.create(UserAccount=secondUser,
                                          DateCharged=date(2017,9,21),
                                          NextBillingDate=date(2017,9,21)+relativedelta(months=+1),
                                          PaymentLevel='s')
        
        # Third User Payments
        UserPaymentHistory.objects.create(UserAccount=thirdUser,
                                          DateCharged=date(2017,9,22),
                                          NextBillingDate=date(2017,9,22)+relativedelta(days=+1),
                                          PaymentLevel='s')
        UserPaymentHistory.objects.create(UserAccount=thirdUser,
                                          DateCharged=date(2017,9,23),
                                          NextBillingDate=date(2017,9,23)+relativedelta(days=+1),
                                          PaymentLevel='s')
        UserPaymentHistory.objects.create(UserAccount=thirdUser,
                                          DateCharged=date(2017,9,24),
                                          NextBillingDate=date(2017,9,24)+relativedelta(days=+1),
                                          PaymentLevel='s')
        
    def test_did_user_get_payment_histories(self):
        firstUser = User.objects.get(username="brian") 
        firstUserPayments = UserPaymentHistory.objects.filter(UserAccount=firstUser)
        self.assertEqual(firstUserPayments.count(), 2)
        
        secondUser = User.objects.get(username="brian2") 
        secondUserPayments = UserPaymentHistory.objects.filter(UserAccount=secondUser)
        self.assertEqual(secondUserPayments.count(), 1)
        
    def test_correct_determination_that_new_payment_is_needed(self):
        firstUser = User.objects.get(username="brian")
        firstUserPayments = UserPaymentHistory.objects.filter(UserAccount=firstUser).last()
        self.assertEqual(firstUserPayments.NewMonthlyPaymentNeeded(), True)
        
        secondUser = User.objects.get(username="brian2") 
        secondUserPayments = UserPaymentHistory.objects.filter(UserAccount=secondUser).last()
        self.assertEqual(secondUserPayments.NewMonthlyPaymentNeeded(), False)
        
        thirdUser = User.objects.get(username="brian3") 
        thirdUserPayments = UserPaymentHistory.objects.filter(UserAccount=thirdUser).last()
        self.assertEqual(thirdUserPayments.NewMonthlyPaymentNeeded(), True)
    
    def test_usersettings_monthly_payment_check(self):
        firstUser = User.objects.get(username="brian")
        firstUserSettings = UserSettings.objects.get(UserAccount=firstUser)
        self.assertEqual(firstUserSettings.CheckIfNewMonthlyPaymentIsNeeded(), True)
        
        secondUser = User.objects.get(username="brian2") 
        secondUserSettings = UserSettings.objects.get(UserAccount=secondUser)
        self.assertEqual(secondUserSettings.CheckIfNewMonthlyPaymentIsNeeded(), False)
        
        thirdUser = User.objects.get(username="brian3")
        thirdUserSettings = UserSettings.objects.get(UserAccount=thirdUser)
        self.assertEqual(thirdUserSettings.CheckIfNewMonthlyPaymentIsNeeded(), False)
        
class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        usd = Currency.objects.create()
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