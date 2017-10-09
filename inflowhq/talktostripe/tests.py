from __future__ import unicode_literals
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from accounts.models import UserSettings
from inflowco.models import Currency
from talktostripe.stripecommunication import StripeCommunication
import stripe
import pytz

class StripeAccountCreationTests(TestCase):
    def setUp(self):
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