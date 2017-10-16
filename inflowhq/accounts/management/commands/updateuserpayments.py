# python3 manage.py updateuserpayments
from django.core.management.base import BaseCommand
from accounts.models import UserSettings

class Command(BaseCommand):
    help = 'Adds a new payment history to all active users'

    def handle(self, *args, **options):
        allActiveUsers = UserSettings.objects.filter(Active=True)
        
        for uSetting in allActiveUsers:
            if uSetting.CheckIfNewMonthlyPaymentIsNeeded():
                uSetting.GenerateNewMonthlyPayment()
                self.stdout.write(self.style.SUCCESS("Generated New Payment For %s" % uSetting.UserAccount.username))