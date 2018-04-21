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

FREELANCER_ANSWER_FREQUENCY = (
    ("f", "Full-Time"),
    ("p", "Part-Time"),
    ("n", "Not currently freelancing")
    )

FREELANCER_WORK_WITH = (
    ("s", "Me, myself, and I"),
    ("t", "Studio/team")
    )

FREELANCER_INTERESTED_IN = (
    ("m", "Milestone Tracking"),
    ("p", "Proposals and Contracts"),
    ("i", "Invoices"),
    ("a", "All of them")
    )

class UserSettings(models.Model):
    UserAccount = models.ForeignKey(User,unique=True,verbose_name="IdAccount",on_delete=models.CASCADE)
    BaseCountry = models.ForeignKey(Country,unique=False,verbose_name="IdBaseCountry",on_delete=models.CASCADE)
    PaymentLevel = models.CharField(max_length=1,
                            choices=PAYMENT_LEVELS,
                            default='s')
    UrlSlug = models.SlugField(max_length=50,null=True)
    StripeApiCustomerKey = models.CharField(max_length=30,null=True)
    StripeConnectAccountKey = models.CharField(max_length=30,null=True)
    FreelancerFrequency = models.CharField(max_length=1,
                            choices=FREELANCER_ANSWER_FREQUENCY,
                            default="n")
    FreelancerWorkWith = models.CharField(max_length=1,
                            choices=FREELANCER_WORK_WITH,
                            default="s")
    FreelancerInterestedIn = models.CharField(max_length=1,
                            choices=FREELANCER_INTERESTED_IN,
                            default="a")
    BusinessName = models.CharField(max_length=50,null=True)
    Region = models.CharField(max_length=50,null=True)
    PhoneNumber = models.CharField(max_length=20,null=True)

    def get_settings_based_on_user(self,loggedin):
        self = UserSettings.objects.filter(UserAccount=loggedin).first()

        if self is None:
            # We will create a new instance of user settings (probably first time log in)
            self = UserSettings()
            self.UserAccount = loggedin

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
            self.UrlSlug = self.generate_slug_for_new_user(loggedin)
            super(UserSettings, self).save()
        
        # In the rare even a slug wasn't created because of much older users, I rather just have the server side code handle it here    
        if self.UrlSlug == "":
            self.UrlSlug = self.generate_slug_for_new_user(loggedin)
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
        elif (lastPayment.NewMonthlyPaymentNeeded()):
            lastPayment = UserPaymentHistory.objects.create(UserAccount=self.UserAccount,
                                                            DateCharged=timezone.now().date(),
                                                            NextBillingDate=timezone.now().date()+relativedelta(months=+1),
                                                            PaymentLevel=self.PaymentLevel)

    def CheckIfNewMonthlyPaymentIsNeeded(self):
        lastPayment = UserPaymentHistory.objects.filter(UserAccount=self.UserAccount).last()

        if (lastPayment is None):
            return (True)
        else:
            return (lastPayment.NewMonthlyPaymentNeeded())

    def generate_slug_for_new_user(self,loggedin):
        generated = slugify("%s %s" % (loggedin.first_name, loggedin.last_name))
        slugs = UserSettings.objects.filter(UrlSlug=generated)

        if len(slugs) == 0:
            return generated
        else:
            return ("%s-%d" % (generated, len(slugs)+1))
    
    def does_this_user_need_stripe(self):
        if self.StripeConnectAccountKey is None:
            return True
        elif self.StripeConnectAccountKey == "":
            return True
        else:
            return False
    
    def __str__(self):
        return self.UserAccount.username

    class Meta:
       db_table = "UserSettings"

class UserPaymentHistory(models.Model):
    UserAccount = models.ForeignKey(User,unique=False,verbose_name="IdAccount",on_delete=models.DO_NOTHING)
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
       db_table = "UserPaymentHistory"

class UserLinkedInInformation(models.Model):
    UserAccount = models.ForeignKey(User,unique=True,verbose_name="IdAccount",on_delete=models.DO_NOTHING)
    LinkedInProfileID = models.CharField(max_length=50,null=False)
    LinkedInAccessToken = models.CharField(max_length=1000,null=False)

    class Meta:
       db_table = "UserLinkedInInformation"

class UserGoogleInformation(models.Model):
    UserAccount = models.ForeignKey(User,unique=True,verbose_name="IdAccount",on_delete=models.DO_NOTHING)
    GoogleProfileID = models.CharField(max_length=50,null=False)
    GoogleProfileName = models.CharField(max_length=150,null=False)
    GoogleImageUrl = models.CharField(max_length=255,null=False)

    class Meta:
       db_table = "UserGoogleInformation"

class UserType(models.Model):
    Name = models.CharField(max_length=50,null=False)
    
    # View Utility Fields
    Selected = False
    
    def __str__(self):
        return self.Name
    
    class Meta:
       db_table = "UserType"
       
class UserAssociatedTypes(models.Model):
    UserAccount = models.ForeignKey(User,verbose_name="IdAccount",on_delete=models.CASCADE)
    UserFreelanceType = models.ForeignKey(UserType,on_delete=models.CASCADE)
    
    class Meta:
       db_table = "UserAssociatedTypes"
    
class NotificationSetting(models.Model):
    SettingName = models.TextField()
    
    class Meta:
       db_table = "NotificationSetting"
       
class UserNotificationSettings(models.Model):
    UserAccount = models.ForeignKey(User,verbose_name="IdAccount",on_delete=models.CASCADE)
    Setting = models.ForeignKey(NotificationSetting,on_delete=models.CASCADE)
    Selected = models.BooleanField()
    
    class Meta:
       db_table = "UserNotificationSettings"