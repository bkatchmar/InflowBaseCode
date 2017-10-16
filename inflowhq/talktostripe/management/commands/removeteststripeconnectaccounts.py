# python3 manage.py removeteststripeconnectaccounts
from django.core.management.base import BaseCommand
from django.conf import settings
import stripe

class Command(BaseCommand):
    help = "Goes into Stripe and removes all custom accounts that we made through unit testing"
    
    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        allTestAccounts = stripe.Account.list()
        allTestCusomters = stripe.Customer.list()
        
        for acctUser in allTestAccounts:
            if ("From Test Case" in acctUser.metadata):
                acctUser.delete()
                print("Deleted %s" % acctUser.id)
                
        for cust in allTestCusomters:
            if ("From Test Case" in cust.metadata):
                cust.delete()
                print("Deleted %s" % cust.id)