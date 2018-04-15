from __future__ import unicode_literals
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from inflowco.models import Country, Currency

CONTRACT_TYPES = (
                  ('d', 'DELIVERABLE BASED'),
                  ('t', 'TIME BASED'),
                  )

CONTRACT_PAYMENT_LEVELS = (
                  ('o', 'ONE TIME'),
                  ('w', 'WEEKLY'),
                  ('b', 'BI WEEKLY'),
                  ('m', 'MONTHLY'),
                  )

RELATIONSHIP_TYPE = (
                  ('f', 'FREELANCER'),
                  ('c', 'CLIENT'),
                  )

CONTRACT_STATES = (
                    ('c', 'Being Created'),
                    ('n', 'Not Started'),
                    ('u', 'Under Review'),
                    ('r', 'Revisions Being Made'),
                    ('p', 'In Progress'),
                    ('x', 'Completed'),
                    )

OWNERSHIP_TYPE = (
                  ('i', 'I own this work'),
                  ('u', 'Client owns this work'),
                  )

class Contract(models.Model):
    Creator = models.ForeignKey(User,unique=False,on_delete=models.CASCADE)
    Name = models.CharField(max_length=200)
    Description = models.TextField(max_length=500,null=True)
    ContractType = models.CharField(max_length=1,choices=CONTRACT_TYPES,default='d')
    StartDate = models.DateField(auto_now=False)
    EndDate = models.DateField(auto_now=False)
    UrlSlug = models.SlugField(max_length=50)
    ContractState = models.CharField(max_length=1,choices=CONTRACT_STATES,default='c')
    Ownership = models.CharField(max_length=1,choices=OWNERSHIP_TYPE,default='i')
    HourlyRate = models.DecimalField(decimal_places=5,null=True,default=0.00000,max_digits=10)
    NumberOfAllowedRevisions = models.PositiveSmallIntegerField(default=1)
    TotalContractWorth = models.DecimalField(decimal_places=5,null=True,default=0.00000,max_digits=10)
    DownPaymentRate = models.DecimalField(decimal_places=5,null=True,default=0.00000,max_digits=10)
    DownPaymentAmount = models.DecimalField(decimal_places=5,null=True,default=0.00000,max_digits=10)

    def create_new_milestone(self):
        newly_created_milestone = Milestone.objects.create(MilestoneContract=self,Name="",Deadline=datetime.date.today())
        return newly_created_milestone

    def create_slug(self):
        self.UrlSlug = slugify('%s' % (self.Name[:50]))
        
    def get_contract_state_view(self):
        for t in CONTRACT_STATES:
            if self.ContractState == t[0]:
                return t[1]
            
        return ""

    def does_this_user_have_permission_to_see_contract(self,loggedinuser):
        relationship = ""

        if (loggedinuser.is_superuser):
            relationship = Relationship.objects.filter(ContractForRelationship=self).first()
        else:
            relationship = Relationship.objects.filter(ContractForRelationship=self,ContractUser=loggedinuser).first()

        return relationship

    def CreatePayment(self,milestoneContractIsBasedOff):
        rtnVal = Payment()
        rtnVal.ContractForPayment = self
        rtnVal.PaymentDate = timezone.now()
        rtnVal.CalculatePayment()
        return rtnVal

    class Meta:
       db_table = 'Contract'

class Recipient(models.Model):
    ContractForRecipient = models.ForeignKey(Contract,unique=True,on_delete=models.CASCADE)
    Name = models.CharField(max_length=200)
    BillingName = models.CharField(max_length=200,null=False)
    PhoneNumber = models.CharField(max_length=20,null=True)
    EmailAddress = models.EmailField()
    
    def create_address_for_recipient(self):
        default_country = Country.objects.first()
        addr = RecipientAddress.objects.create(RecipientForAddress=self,Address1="",Address2="",State="",City="",Country=default_country) 
        return addr

    class Meta:
       db_table = 'ContractRecipient'

class RecipientAddress(models.Model):
    RecipientForAddress = models.ForeignKey(Recipient,unique=False,on_delete=models.CASCADE)
    Address1 = models.CharField(max_length=200)
    Address2 = models.CharField(max_length=200)
    State = models.CharField(max_length=100)
    City = models.CharField(max_length=200)
    Country = models.ForeignKey(Country,unique=False,null=True,on_delete=models.SET_NULL)
    
    class Meta:
       db_table = 'ContractRecipientAddress'

class Milestone(models.Model):
    IdMilestone = models.AutoField(primary_key=True,verbose_name="IdMilestone")
    MilestoneContract = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    Name = models.CharField(max_length=200)
    Explanation = models.TextField()
    MilestonePaymentAmount = models.DecimalField(decimal_places=5,null=False,default=0.00000,max_digits=10)
    EstimateHoursRequired = models.DecimalField(decimal_places=5,null=False,default=0.00000,max_digits=10)
    Deadline = models.DateField(auto_now=False)

    class Meta:
       db_table = 'Milestone'

class Relationship(models.Model):
    ContractUser = models.ForeignKey(User,unique=False,on_delete=models.CASCADE)
    ContractForRelationship = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    RelationshipType = models.CharField(max_length=1,choices=RELATIONSHIP_TYPE,default='f')

    class Meta:
       db_table = 'ContractRelationship'

class PaymentPlan(models.Model):
    ContractForPaymentPlan = models.ForeignKey(Contract,unique=True,on_delete=models.CASCADE)
    PaymentType = models.CharField(max_length=1,choices=CONTRACT_PAYMENT_LEVELS,default='o')
    ContractCurrency = models.ForeignKey(Currency,unique=False,on_delete=models.CASCADE)
    TotalPaymentAmount = models.DecimalField(decimal_places=2,null=True,max_digits=10)

    class Meta:
       db_table = 'ContractPaymentPlan'

class Payment(models.Model):
    ContractForPayment = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    PaymentDate = models.DateField(auto_now=False)
    Amount = models.DecimalField(decimal_places=2,null=False,default=0.00,max_digits=10)

    def CalculatePayment(self):
        rtnVal.Amount = 0.00

    class Meta:
       db_table = 'ContractPayment'
