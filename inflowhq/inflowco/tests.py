from __future__ import unicode_literals
# References from our own library
from inflowco.models import Currency, EmailSignup
# Django references
from django.contrib.auth.models import User
from django.test import Client, TestCase
import pytz

class BaseEmailSignUpCase(TestCase):
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
        signups = len(EmailSignup.objects.all())
        self.assertEqual(0, signups)
        
    def test_email_signup_homepage(self):
        c = Client()
        response = c.post("", {"email-address" : "Brian@workinflow.co"})
        signups = len(EmailSignup.objects.all())
        
        self.assertNotEqual(response.context["sign_up_msg"], "")
        self.assertGreater(signups, 0)
        
    def test_how_it_works_context(self):
        c = Client()
        response = c.get("/how-it-works")
        
        self.assertEqual(response.context["active_link"], "how it works")
    
    def test_about_us_context(self):
        c = Client()
        response = c.get("/about-inflow")
        
        self.assertEqual(response.context["active_link"], "about us")
        
class TestInFlowDashboardScreens(TestCase):
    def setUp(self):
        # Brian - User 1
        brian = User.objects.create(
                            username="brian",
                            email="brian@workinflow.co",
                            password="th3l10nK1ng15Fun",
                            first_name="Brian",
                            last_name="Katchmar",
                            is_staff=True,
                            is_active=True,
                            is_superuser=True)
        brian.set_password("th3l10nK1ng15Fun")
        brian.save()
        
        # Kenny - User 2
        kenny = User.objects.create(
                            username="kenny",
                            email="kenny@workinflow.co",
                            password="th3l10nK1ng15Funner",
                            first_name="Kenny",
                            last_name="Kim",
                            is_staff=True,
                            is_active=True,
                            is_superuser=True)
        kenny.set_password("th3l10nK1ng15Funner")
        kenny.save()
    
    def test_context_user_1(self):
        c = Client()
        loginAttempt = c.login(username='brian', password='th3l10nK1ng15Fun')
        response = c.get('/inflow/')
        
        self.assertTrue(loginAttempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        self.assertEqual("Brian",response.context["first_name"])
        
    def test_context_user_2(self):
        c = Client()
        loginAttempt = c.login(username='kenny', password='th3l10nK1ng15Funner')
        response = c.get('/inflow/')
        
        self.assertTrue(loginAttempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        self.assertEqual("Kenny",response.context["first_name"])