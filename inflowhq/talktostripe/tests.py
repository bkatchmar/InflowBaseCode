from __future__ import unicode_literals
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase, Client
from django.utils import timezone
from accounts.models import UserSettings
from inflowco.models import Currency
from talktostripe.stripecommunication import StripeCommunication
import pytz
import stripe
import time as _time

class StripeAccountCreationTests(TestCase):
    def setUp(self):
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        usd = Currency.objects.create()
        timezone.activate(pytz.timezone("America/New_York"))
        
        # Users
        user1 = User.objects.create(username="stripeuser1",email="stripeuser1@workinflow.co",first_name="Josh",last_name="Blank",is_staff=False,is_active=True,is_superuser=False)
        user1.set_password("password2")
        user1.save()
        
        user2 = User.objects.create(username="stripeuser2",email="stripeuser2@workinflow.co",first_name="Matthew",last_name="Stewart",is_staff=False,is_active=True,is_superuser=False)
        user2.set_password("password3")
        user2.save()
        
        # Get Settings
        date_first = date(2017,10,12)
        time_first = time(12, 0, 0, tzinfo=timezone.get_current_timezone())
        aware_datetime_first = datetime.combine(date_first, time_first)
        settings1 = UserSettings.objects.create(UserAccount=user1,
                                    Active=True,
                                    Joined=aware_datetime_first,
                                    BaseCurrency=usd,
                                    PaymentLevel='s')
        
        date_second = date(2017,10,10)
        aware_datetime_second = datetime.combine(date_second, time_first)
        settings2 = UserSettings.objects.create(UserAccount=user2,
                                    Active=True,
                                    Joined=aware_datetime_second,
                                    BaseCurrency=usd,
                                    PaymentLevel='s')
        
        comm = StripeCommunication()
        comm.CreateNewStripeCustomerWithId(settings1,fromtestcase=True)
        comm.CreateNewStripeCustomerWithId(settings2,fromtestcase=True)
        
        comm.CreateNewStripeCustomAccount(settings1,fromtestcase=True)
        comm.CreateNewStripeCustomAccount(settings2,fromtestcase=True)
        
        # Custom Stripe Account Information
        accountFromStripeQuery1 = stripe.Account.retrieve(settings1.StripeConnectAccountKey)
        accountFromStripeQuery2 = stripe.Account.retrieve(settings2.StripeConnectAccountKey)
        
        accountFromStripeQuery1 = stripe.Account.retrieve(settings1.StripeConnectAccountKey)
        accountFromStripeQuery1.legal_entity.dob.day = 30
        accountFromStripeQuery1.legal_entity.dob.month = 7
        accountFromStripeQuery1.legal_entity.dob.year = 1986
        accountFromStripeQuery1.legal_entity.type = "individual"
        accountFromStripeQuery1.legal_entity.address.line1 = "123 Anywhere Lane"
        accountFromStripeQuery1.legal_entity.address.city = "New York"
        accountFromStripeQuery1.legal_entity.address.state = "New York"
        accountFromStripeQuery1.legal_entity.address.postal_code = 10001
        accountFromStripeQuery1.tos_acceptance.date = int(_time.time())
        accountFromStripeQuery1.tos_acceptance.ip = "8.8.8.8"
        accountFromStripeQuery1.save()
        
        accountFromStripeQuery2 = stripe.Account.retrieve(settings2.StripeConnectAccountKey)
        accountFromStripeQuery2.legal_entity.dob.day = 6
        accountFromStripeQuery2.legal_entity.dob.month = 3
        accountFromStripeQuery2.legal_entity.dob.year = 1990
        accountFromStripeQuery2.legal_entity.type = "company"
        accountFromStripeQuery2.legal_entity.address.line1 = "456 Other Circle"
        accountFromStripeQuery2.legal_entity.address.city = "New York"
        accountFromStripeQuery2.legal_entity.address.state = "New York"
        accountFromStripeQuery2.legal_entity.address.postal_code = 10001
        accountFromStripeQuery2.tos_acceptance.date = int(_time.time())
        accountFromStripeQuery2.tos_acceptance.ip = "8.8.8.8"
        accountFromStripeQuery2.save()
        
    def test_stripe_calls(self):
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        stripeuser1 = User.objects.get(username="stripeuser1")
        stripeuser2 = User.objects.get(username="stripeuser2")
        
        settings1 = UserSettings.objects.get(UserAccount=stripeuser1)
        settings2 = UserSettings.objects.get(UserAccount=stripeuser2)
        
        userFromStripeQuery1 = stripe.Customer.retrieve(settings1.StripeApiCustomerKey)
        userFromStripeQuery2 = stripe.Customer.retrieve(settings2.StripeApiCustomerKey)
        
        self.assertIsNotNone(settings1.StripeApiCustomerKey)
        self.assertEqual(userFromStripeQuery1["id"], settings1.StripeApiCustomerKey)
        self.assertEqual(userFromStripeQuery2["id"], settings2.StripeApiCustomerKey)
        
        # Remove the users from Stripe
        userFromStripeQuery1.delete()
        userFromStripeQuery2.delete()
        
        self.assertTrue(userFromStripeQuery1["deleted"])
        self.assertTrue(userFromStripeQuery2["deleted"])
    
    def test_stripe_screens_user_kicked_out(self):
        c = Client()
        response1 = c.get('/inflow/stripe/')
        self.assertEqual(302,response1.status_code)
        
        response2 = c.get('/inflow/stripe/stripe-setup/')
        self.assertEqual(302,response2.status_code)
    
    def test_stripe_account_creation_and_screens_1(self):
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        stripeuser1 = User.objects.get(username="stripeuser1")
        settings1 = UserSettings.objects.get(UserAccount=stripeuser1)
        accountFromStripeQuery1 = stripe.Account.retrieve(settings1.StripeConnectAccountKey)
        
        c = Client()
        loginAttempt = c.login(username='stripeuser1', password='password2')
        response = c.get('/inflow/stripe/stripe-setup/')
        
        self.assertEqual(response.context["legalEntityType"], "individual")
        self.assertEqual(response.context["legalEntityAddress"]["line1"], "123 Anywhere Lane")
        self.assertEqual(response.context["legalEntityAddress"]["city"], "New York")
        self.assertEqual(response.context["legalEntityAddress"]["state"], "New York")
        self.assertEqual(response.context["legalEntityAddress"]["postal_code"], "10001")
        self.assertEqual(response.context["legalEntityDob"]["year"], 1986)
        self.assertEqual(response.context["legalEntityDob"]["month"], 7)
        self.assertEqual(response.context["legalEntityDob"]["day"], 30)
        self.assertEqual(response.context["legalEntityDob"]["zeroBasedIndexMonth"], 6)
        self.assertEqual(200,response.status_code)
        
        accountFromStripeQuery1.delete()
        
    def test_stripe_account_creation_and_screens_2(self):
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        stripeuser2 = User.objects.get(username="stripeuser2")
        settings2 = UserSettings.objects.get(UserAccount=stripeuser2)
        accountFromStripeQuery2 = stripe.Account.retrieve(settings2.StripeConnectAccountKey)

        c = Client()
        loginAttempt = c.login(username='stripeuser2', password='password3')
        response = c.get('/inflow/stripe/stripe-setup/')
        
        self.assertEqual(response.context["legalEntityType"], "company")
        self.assertEqual(200,response.status_code)
        
        accountFromStripeQuery2.delete()