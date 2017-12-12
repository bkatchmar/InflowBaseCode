from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from inflowco.models import Currency

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

MILESTONE_PAYMENT_TYPE = (
                  ('r', 'RAW AMOUNT'),
                  ('p', 'PERCENTAGE'),
                  )

RELATIONSHIP_TYPE = (
                  ('f', 'FREELANCER'),
                  ('c', 'CLIENT'),
                  )

class Contract(models.Model):
    Creator = models.ForeignKey(User,unique=False,on_delete=models.CASCADE)
    Name = models.CharField(max_length=200)
    ContractType = models.CharField(max_length=1,choices=CONTRACT_TYPES,default='d')
    StartDate = models.DateField(auto_now=True)
    EndDate = models.DateField(auto_now=True)
    UrlSlug = models.SlugField(max_length=50)

    def CreateNewMilestone(self):
        newlyCreated = Milestone.objects.create(MilestoneContract=self)
        return newlyCreated

    def CreateSlug(self):
        self.UrlSlug = slugify('%s' % (self.Name[:50]))

    def DoesThisUserHavePermissionToSeeContract(self,loggedinuser):
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
    Address = models.CharField(max_length=200)
    State = models.CharField(max_length=100)
    Email = models.EmailField()
    City = models.CharField(max_length=200)
    Country = models.CharField(max_length=100)

    class Meta:
       db_table = 'ContractRecipient'

class Milestone(models.Model):
    IdMilestone = models.AutoField(primary_key=True,verbose_name="IdMilestone")
    MilestoneContract = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    Explanation = models.TextField()
    MilestonePaymentAmount = models.DecimalField(decimal_places=5,null=False,default=0.00000,max_digits=10)
    MilestonePaymentType = models.CharField(max_length=1,choices=MILESTONE_PAYMENT_TYPE,default='r')
    NumberOfAllowedRevisions = models.PositiveSmallIntegerField(default=1)

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
