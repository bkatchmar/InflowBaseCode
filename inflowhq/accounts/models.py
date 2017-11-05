from __future__ import unicode_literals
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from inflowco.models import Country, Currency

PAYMENT_LEVELS = (
                  ('s', 'standard'),
                  )

class UserSettings(models.Model):
    UserAccount = models.ForeignKey(User,unique=True,verbose_name="IdAccount")
    Active = models.BooleanField(default=True,verbose_name="Active")
    Joined = models.DateTimeField(default=timezone.now,verbose_name="Joined")
    BaseCountry = models.ForeignKey(Country,unique=False,verbose_name="IdBaseCountry")
    PaymentLevel = models.CharField(max_length=1,
                            choices=PAYMENT_LEVELS,
                            default='s')
    UrlSlug = models.SlugField(max_length=50,null=True)
    StripeApiCustomerKey = models.CharField(max_length=30,null=True)
    StripeConnectAccountKey = models.CharField(max_length=30,null=True)
    
    def GetSettingsBasedOnUser(self,loggedin):
        self = UserSettings.objects.filter(UserAccount=loggedin).first()

        if self is None:
            # We will create a new instance of user settings (probably first time log in)
            self = UserSettings()
            self.UserAccount = loggedin
            self.Active = UserSettings._meta.get_field('Active').get_default()
            self.Joined = UserSettings._meta.get_field('Joined').get_default()
            
            BaseCurrency = Currency()
            BaseCurrency.IdCurrency = Currency._meta.get_field('IdCurrency').get_default()
            BaseCurrency.Country = Currency._meta.get_field('Country').get_default()
            BaseCurrency.Name = Currency._meta.get_field('Name').get_default()
            BaseCurrency.Code = Currency._meta.get_field('Code').get_default()
            
            self.BaseCountry = Country()
            self.BaseCountry.IdCountry = Country._meta.get_field('IdCountry').get_default()
            self.BaseCountry.Name = Country._meta.get_field('Name').get_default()
            self.BaseCountry.Code = Country._meta.get_field('Code').get_default()
            self.BaseCountry.PrimaryCurrency = BaseCurrency
            self.PaymentLevel = 's'
            self.UrlSlug = slugify('%s %s' % (loggedin.first_name, loggedin.last_name))
            super(UserSettings, self).save()
            
        return self
    
    def GenerateNewMonthlyPayment(self):
        lastPayment = UserPaymentHistory.objects.filter(UserAccount=self.UserAccount).last()
        
        if (lastPayment is None):
            lastPayment = UserPaymentHistory()
            lastPayment.DateCharged = timezone.now().date()
            lastPayment.NextBillingDate = lastPayment.DateCharged+relativedelta(months=+1)
            lastPayment.UserAccount = self.UserAccount
            lastPayment.PaymentLevel = self.PaymentLevel
            super(UserPaymentHistory, lastPayment).save()
        elif (lastPayment.NewMonthlyPaymentNeeded() and self.Active):
            lastPayment = UserPaymentHistory.objects.create(UserAccount=self.UserAccount,
                                                            DateCharged=timezone.now().date(),
                                                            NextBillingDate=timezone.now().date()+relativedelta(months=+1),
                                                            PaymentLevel=self.PaymentLevel)
    
    def CheckIfNewMonthlyPaymentIsNeeded(self):
        lastPayment = UserPaymentHistory.objects.filter(UserAccount=self.UserAccount).last()
        
        if (lastPayment is None):
            return (self.Active)
        else:
            return (lastPayment.NewMonthlyPaymentNeeded() and self.Active)
    
    def __str__(self):
        return self.UserAccount.username
    
    class Meta:
       db_table = 'UserSettings'
    
class UserPaymentHistory(models.Model):
    UserAccount = models.ForeignKey(User,unique=False,verbose_name="IdAccount")
    DateCharged = models.DateField(auto_now=False,verbose_name="DateCharged")
    NextBillingDate = models.DateField(verbose_name="NextBillingDate")
    PaymentLevel = models.CharField(max_length=1,
                            choices=PAYMENT_LEVELS,
                            default='s')
    PaymentAmount=models.DecimalField(decimal_places=2,verbose_name="PaymentAmount",null=False,default=16.00,max_digits=6)
    
    def NewMonthlyPaymentNeeded(self):
        if (isinstance(self.NextBillingDate, datetime)):
            self.NextBillingDate = self.NextBillingDate.date()
        if (isinstance(self.DateCharged, datetime)):
            self.DateCharged = self.DateCharged.date()
        
        if (self.NextBillingDate < timezone.now().date()):
            return True
        elif (self.NextBillingDate == timezone.now().date()):
            lastPayment = UserPaymentHistory.objects.filter(DateCharged=timezone.now().date()).last()
            return (lastPayment is None)
        else:
            return False
    
    class Meta:
       db_table = 'UserPaymentHistory'
       
class UserLinkedInInformation(models.Model):
    UserAccount = models.ForeignKey(User,unique=True,verbose_name="IdAccount")
    LinkedInProfileID = models.CharField(max_length=50,null=False)
    LinkedInAccessToken = models.CharField(max_length=1000,null=False)
    
    class Meta:
       db_table = 'UserLinkedInInformation'