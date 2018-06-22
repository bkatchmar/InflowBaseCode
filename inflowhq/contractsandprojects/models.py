from __future__ import unicode_literals
import datetime
from decimal import Decimal
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
                    ('u', 'Under Review'),
                    ('r', 'Revisions Being Made'),
                    ('n', 'Not Started'),
                    ('p', 'In Progress'),
                    ('x', 'Completed'),
                    )

MILESTONE_STATES = (
                    ('n', 'Not Started'),
                    ('p', 'In Progress'),
                    ('x', 'Completed'),
                    )

OWNERSHIP_TYPE = (
                  ('i', 'I own this work'),
                  ('u', 'Client owns this work'),
                  )

MILESTONE_REACTIONS = (
                  ('a', 'Accept'),
                  ('r', 'Reject'),
                  )

TIME_WINDOW_TOLERANCE = (
                  ('d', 'Per Day'),
                  ('w', 'Per Week'),
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
    NumberOfAllowedRevisions = models.PositiveSmallIntegerField(default=3)
    TotalContractWorth = models.DecimalField(decimal_places=5,null=True,default=0.00000,max_digits=10)
    DownPaymentRate = models.DecimalField(decimal_places=5,null=True,default=0.00000,max_digits=10)
    DownPaymentAmount = models.DecimalField(decimal_places=5,null=True,default=0.00000,max_digits=10)
    ExtraRevisionFee = models.DecimalField(decimal_places=2,null=True,default=0.00000,max_digits=10)
    RequestForChangeFee = models.DecimalField(decimal_places=2,null=True,default=0.00000,max_digits=10)
    ChargeForLateReview = models.DecimalField(decimal_places=2,null=True,default=0.00000,max_digits=10)
    KillFee = models.DecimalField(decimal_places=2,null=True,default=0.00,max_digits=10)
    FreelancerPortfolioPiece = models.CharField(max_length=50,null=True)

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
    
    def get_contract_text(self):
        paragraphs = ContractText.objects.filter(ContractFor=self)
        
        if len(paragraphs) == 0:
            paragraphs = []
            paragraphs.append(ContractText.objects.create(ContractFor=self,Order=1,ParagraphText='I. Icing bear claw wafer. Tart bonbon muffin jelly-o. Sesame snaps lemon drops sugar plum toffee caramels. Pudding sesame snaps tiramisu lemon drops jelly. Halvah gummi bears sugar plum danish tootsie roll. Jelly lollipop bear claw cookie gummies icing. Caramels carrot cake pie chupa chups dragée chupa chups wafer. Dessert chupa chups chupa chups. Cake tiramisu sweet roll tiramisu chocolate cake lollipop cupcake gummi bears chocolate cake. Pastry cake cupcake donut gingerbread chocolate cake cheesecake bear claw. Halvah biscuit wafer bear claw chocolate bar bonbon lollipop apple pie. Chocolate icing croissant chocolate bar dessert.'))
            paragraphs.append(ContractText.objects.create(ContractFor=self,Order=2,ParagraphText='II. Donut cake gummies gingerbread croissant. Apple pie sugar plum brownie pie. Jelly marzipan dessert sugar plum marzipan soufflé. Wafer candy canes ice cream candy oat cake macaroon wafer sesame snaps candy. Tart toffee biscuit donut fruitcake. Jelly-o brownie brownie croissant tootsie roll sesame snaps gingerbread. Lollipop jelly-o gummies cake cotton candy jelly caramels danish ice cream. Jelly-o chocolate dessert icing topping. Sweet roll gingerbread jujubes. Jelly-o fruitcake bonbon chocolate bar liquorice icing ice cream gingerbread bonbon. Biscuit cupcake sesame snaps cotton candy sweet roll. Liquorice chocolate cake ice cream lollipop lemon drops. Caramels bonbon sweet roll candy canes oat cake donut chocolate sweet cake.'))
            paragraphs.append(ContractText.objects.create(ContractFor=self,Order=3,ParagraphText='III. Marzipan apple pie tiramisu cake. Macaroon tootsie roll donut candy soufflé. Brownie wafer topping jujubes sugar plum jelly carrot cake. Macaroon candy chupa chups. Halvah jelly halvah jelly-o. Gummies dessert pastry cheesecake pudding icing tiramisu candy. Chocolate caramels sweet roll cupcake ice cream. Caramels cotton candy tart bonbon topping wafer caramels icing lollipop. Candy chocolate cake cheesecake halvah liquorice jelly-o chupa chups lemon drops. Jelly cheesecake sweet. Macaroon cookie pie. Dessert donut soufflé powder danish halvah powder soufflé candy canes.'))
            paragraphs.append(ContractText.objects.create(ContractFor=self,Order=4,ParagraphText='IV. Icing bear claw wafer. Tart bonbon muffin jelly-o. Sesame snaps lemon drops sugar plum toffee caramels. Pudding sesame snaps tiramisu lemon drops jelly. Halvah gummi bears sugar plum danish tootsie roll. Jelly lollipop bear claw cookie gummies icing. Caramels carrot cake pie chupa chups dragée chupa chups wafer. Dessert chupa chups chupa chups. Cake tiramisu sweet roll tiramisu chocolate cake lollipop cupcake gummi bears chocolate cake. Pastry cake cupcake donut gingerbread chocolate cake cheesecake bear claw. Halvah biscuit wafer bear claw chocolate bar bonbon lollipop apple pie. Chocolate icing croissant chocolate bar dessert.'))
        
        return paragraphs

    def does_this_user_have_permission_to_see_contract(self,loggedinuser):
        relationship = ""

        if (loggedinuser.is_superuser):
            relationship = Relationship.objects.filter(ContractForRelationship=self).first()
        else:
            relationship = Relationship.objects.filter(ContractForRelationship=self,ContractUser=loggedinuser).first()

        return relationship
    
    def is_the_user_the_creator_of_contract(self,loggedinuser):
        if (loggedinuser.is_superuser):
            return True
        elif self.Creator.id == loggedinuser.id:
            return True
        else:
            return False
    
    def is_the_user_a_freelancer(self,loggedinuser):
        if (loggedinuser.is_superuser):
            return True
        elif Relationship.objects.filter(ContractForRelationship=self,ContractUser=loggedinuser,RelationshipType="f").exists():
            return True
        else:
            return False
    
    def is_the_user_a_client(self,loggedinuser):
        if (loggedinuser.is_superuser):
            return True
        elif Relationship.objects.filter(ContractForRelationship=self,ContractUser=loggedinuser,RelationshipType="c").exists():
            return True
        else:
            return False
    
    def calculate_time_left_string(self):
        diff = self.EndDate - timezone.now().date()
        
        if diff.days == 0:
            return "0 Days"
        else:
            # Perform calculations
            weeks = int(diff.days / 7)
            remaining_days = diff.days % 7
            
            # Since I rather declare my variables before I assign them most of the time
            weeks_str = ""
            days_str = ""
            
            # Logic to determine what the above strings will read as
            if weeks == 1:
                weeks_str = "1 Week"
            elif weeks > 1:
                weeks_str = ("%d Weeks" % weeks)
            else:
                weeks_str = ""
                
            if remaining_days == 0:
                days_str = ""
                return weeks_str
            elif weeks >= 1:
                days_str = (", %d Days" % remaining_days)
            else:
                return ("%d Days" % remaining_days)
            
            return ("%s%s" % (weeks_str, days_str))
    
    def delete_milestone_if_exists(self,milestone_id):
        if milestone_id != 0:
            milestone_to_delete = Milestone.objects.filter(IdMilestone=milestone_id).first()
            
            if milestone_to_delete is not None:
                milestone_to_delete.delete()

    def CreatePayment(self,milestoneContractIsBasedOff):
        rtnVal = Payment()
        rtnVal.ContractForPayment = self
        rtnVal.PaymentDate = timezone.now()
        rtnVal.CalculatePayment()
        return rtnVal

    class Meta:
       db_table = "Contract"
    
class ContractFile(models.Model):
    ContractForFile = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    FileName = models.CharField(max_length=100)
    FileURL = models.CharField(max_length=200)
    FileExtension = models.CharField(max_length=10)
    FileUploaded = models.DateField(auto_now=False)
    SizeOfFile = models.CharField(max_length=10)
    
    class Meta:
       db_table = 'ContractFile'
       
class ContractLateReviewCharge(models.Model):
    ContractForCharge = models.ForeignKey(Contract,unique=True,on_delete=models.CASCADE)
    DaysLateTolerance = models.IntegerField(null=False)
    Charge = models.DecimalField(decimal_places=3,null=False,default=0.000,max_digits=10)
    TimeWindowToleranceType = models.CharField(max_length=1,choices=TIME_WINDOW_TOLERANCE,default='d')
    
    def get_window_value_view(self):
        for window in TIME_WINDOW_TOLERANCE:
            if self.TimeWindowToleranceType == window[0]:
                return window[1]
    
    class Meta:
       db_table = "ContractLateReviewCharge"

class ContractAmendmentSet(models.Model):
    ContractAmended = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    Proposer = models.ForeignKey(User,unique=False,on_delete=models.CASCADE)
    DateSubmitted = models.DateTimeField(auto_now=False,auto_now_add=False)
    
    class Meta:
       db_table = "ContractAmendmentSet"
       
class ContractAmendment(models.Model):
    Set = models.ForeignKey(ContractAmendmentSet,unique=False,on_delete=models.CASCADE)
    Field = models.CharField(max_length=50,null=False)
    ChangeFrom = models.TextField()
    ChangeTo = models.TextField()
    ReasonForChange = models.TextField()
    SystemGeneratedMessage = models.TextField()
    
    class Meta:
       db_table = "ContractAmendment"

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
    ZipCode = models.CharField(max_length=20,null=True)
    
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
    MilestoneState = models.CharField(max_length=1,choices=MILESTONE_STATES,default='n')
    ScheduledDeliveryDate = models.DateField(auto_now=False,null=True)
    Delivered = models.DateField(auto_now=False,null=True)
    
    def get_milestone_state_view(self):
        for t in MILESTONE_STATES:
            if self.MilestoneState == t[0]:
                return t[1]
            
        return ""
    
    def get_stripe_transaction_fee(self,stripe_rate=0.029):
        return (self.MilestonePaymentAmount * Decimal(stripe_rate))
    
    def get_sales_tax(self,sales_tax=0.08875):
        return (self.MilestonePaymentAmount * Decimal(sales_tax))
    
    def get_total_payment(self,stripe_rate=0.029,sales_tax=0.08875):
        return self.MilestonePaymentAmount + self.get_stripe_transaction_fee(stripe_rate) + self.get_sales_tax(sales_tax)

    class Meta:
       db_table = 'Milestone'

class Relationship(models.Model):
    ContractUser = models.ForeignKey(User,unique=False,on_delete=models.CASCADE)
    ContractForRelationship = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    RelationshipType = models.CharField(max_length=1,choices=RELATIONSHIP_TYPE,default='f')

    class Meta:
       db_table = 'ContractRelationship'

class ContractText(models.Model):
    ContractFor = models.ForeignKey(Contract,unique=False,on_delete=models.CASCADE)
    ParagraphText = models.TextField(null=True)
    Order = models.PositiveSmallIntegerField(default=1)
    
    class Meta:
       db_table = "ContractText"
    
class MilestoneFile(models.Model):
    MilestoneForFile = models.ForeignKey(Milestone,unique=False,on_delete=models.CASCADE)
    FileName = models.CharField(max_length=100)
    FileURL = models.CharField(max_length=200)
    FilePreviewURL = models.CharField(max_length=200)
    FileExtension = models.CharField(max_length=10)
    
    class Meta:
       db_table = "MilestoneFile"
       
class MilestoneReaction(models.Model):
    MilestoneForReaction = models.ForeignKey(Milestone,unique=False,null=False,on_delete=models.CASCADE)
    UserReacting = models.ForeignKey(User,unique=False,null=False,on_delete=models.CASCADE)
    Comment = models.TextField(null=False)
    ReactionType = models.CharField(max_length=1,null=False,choices=MILESTONE_REACTIONS,default='a')
    ReactionDateTime = models.DateTimeField(auto_now=False,auto_now_add=False)
    
    class Meta:
       db_table = "MilestoneReaction"

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