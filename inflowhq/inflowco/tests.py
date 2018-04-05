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