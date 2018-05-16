from __future__ import unicode_literals
from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone
from inflowco.models import Currency, Country
from contractsandprojects.models import Contract, Milestone, Payment, PaymentPlan, Recipient, Relationship, ContractText
import pytz

class ContractScreenAuthenticationTestCase(TestCase):
    def setUp(self):
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        brianUser = User.objects.create(
                            username="brian",
                            email="brian@workinflow.co",
                            first_name="Brian",
                            last_name="Katchmar",
                            is_staff=True,
                            is_active=True,
                            is_superuser=True)
        
        brianUser.set_password("ilikechickenfingersandpizza")
        brianUser.save()
    
    def test_not_logged_in_user_get_kicked_out(self):
        c = Client()
        response = c.get('/inflow/projects/')
        self.assertEqual(302,response.status_code)
        
    def test_does_user_see_page_when_logged_in(self):
        c = Client()
        loginAttempt = c.login(username='brian', password='ilikechickenfingersandpizza')
        response = c.get('/inflow/projects/')
        
        self.assertTrue(loginAttempt) # User was able to log in
        self.assertEqual(200,response.status_code) # User can see the page
        
class ContractAndMilestoneModelCreationTest(TestCase):
    def setUp(self):
        usd = Currency.objects.create()
        timezone.activate(pytz.timezone("America/New_York"))
        
        brianUser = User.objects.create(
                            username="brian",
                            email="brian@workinflow.co",
                            first_name="Brian",
                            last_name="Katchmar",
                            is_staff=True,
                            is_active=True,
                            is_superuser=True)
        
        brianUser.set_password("ilikechickenfingersandpizza")
        brianUser.save()
        
        firstContract = Contract.objects.create(
                            Creator=brianUser,
                            Name="Brian First Project",
                            StartDate=date(2017,9,20),
                            EndDate=date(2017,9,29))
        
        firstContract.create_slug()
        firstContract.save()
        
        firstContract.create_new_milestone()
        firstContract.create_new_milestone()
        firstContract.create_new_milestone()
        
        # Second contract, this is meant to test the 50 character slug limit but over 50 character name
        secondContract = Contract.objects.create(
                            Creator=brianUser,
                            Name="I Like Chicken Fingers, Bacon, Pizza, Ice Cream, and Cereal",
                            StartDate=date(2017,10,2),
                            EndDate=date(2017,10,5))
        
        secondContract.create_slug()
        secondContract.save()
        
        secondContract.create_new_milestone()
        secondContract.create_new_milestone()
        
        # Contract Recipients
        Recipient.objects.create(ContractForRecipient=firstContract,Name="John Smith",BillingName="John Smith")
        Recipient.objects.create(ContractForRecipient=secondContract,Name="Jane Doe",BillingName="Jane Doe")
        
        # Contract Payment Plan
        PaymentPlan.objects.create(ContractForPaymentPlan=firstContract,ContractCurrency=usd)
        PaymentPlan.objects.create(ContractForPaymentPlan=secondContract,ContractCurrency=usd)
        
    def test_does_proper_slug_get_created(self):
        firstContract = Contract.objects.get(Name="Brian First Project")
        self.assertEqual(firstContract.UrlSlug, "brian-first-project")
        
    def test_slug_limit(self):
        secondContract = Contract.objects.get(Name="I Like Chicken Fingers, Bacon, Pizza, Ice Cream, and Cereal")
        self.assertEqual(secondContract.UrlSlug, "i-like-chicken-fingers-bacon-pizza-ice-cream-a")
        
    def test_milestone_creation(self):
        firstContract = Contract.objects.get(Name="Brian First Project")
        secondContract = Contract.objects.get(Name="I Like Chicken Fingers, Bacon, Pizza, Ice Cream, and Cereal")
        
        firstContractMilestones = Milestone.objects.filter(MilestoneContract=firstContract)
        self.assertEqual(firstContractMilestones.count(), 3)
        
        secondContractMilestones = Milestone.objects.filter(MilestoneContract=secondContract)
        self.assertEqual(secondContractMilestones.count(), 2)
        
class ContractRelationshipTest(TestCase):
    def setUp(self):
        usd = Currency.objects.create()
        timezone.activate(pytz.timezone("America/New_York"))
        
        # Users
        user1 = User.objects.create(username="brian",email="brian@workinflow.co",first_name="Brian",last_name="Katchmar",is_staff=True,is_active=True,is_superuser=True)
        user1.set_password("password1")
        user1.save()
        
        user2 = User.objects.create(username="josh",email="josh@workinflow.co",first_name="Josh",last_name="Blank",is_staff=False,is_active=True,is_superuser=False)
        user2.set_password("password2")
        user2.save()
        
        user3 = User.objects.create(username="matt",email="matt@workinflow.co",first_name="Matthew",last_name="Stewart",is_staff=False,is_active=True,is_superuser=False)
        user3.set_password("password3")
        user3.save()
        
        user4 = User.objects.create(username="erin",email="erin@workinflow.co",first_name="Erin",last_name="Pienta",is_staff=False,is_active=True,is_superuser=False)
        user4.set_password("password4")
        user4.save()
        
        user5 = User.objects.create(username="kenny",email="kenny@workinflow.co",first_name="Kenny",last_name="Kim",is_staff=False,is_active=True,is_superuser=False)
        user5.set_password("password5")
        user5.save()
        
        user6 = User.objects.create(username="clara",email="clara@workinflow.co",first_name="Clara",last_name="Chang",is_staff=False,is_active=True,is_superuser=False)
        user6.set_password("password6")
        user6.save()
        
        # Contracts
        contract1 = Contract.objects.create(Creator=user2,Name="Josh Contract",StartDate=date(2017,10,5),EndDate=date(2017,10,15))
        contract1.create_slug()
        contract1.save()
        
        contract2 = Contract.objects.create(Creator=user4,Name="Erin Contract",StartDate=date(2017,10,16),EndDate=date(2017,10,25))
        contract2.create_slug()
        contract2.save()
        
        # Contract Recipients
        Recipient.objects.create(ContractForRecipient=contract1,Name="Brian Katchmar",BillingName="John Smith")
        Recipient.objects.create(ContractForRecipient=contract2,Name="Brian Katchmar",BillingName="John Smith")
        
        # Contract Payment Plan
        PaymentPlan.objects.create(ContractForPaymentPlan=contract1,ContractCurrency=usd)
        PaymentPlan.objects.create(ContractForPaymentPlan=contract2,ContractCurrency=usd)
        
        # Contract Relationship
        Relationship.objects.create(ContractUser=user2,ContractForRelationship=contract1,RelationshipType='f')
        Relationship.objects.create(ContractUser=user3,ContractForRelationship=contract1,RelationshipType='c')
        
        Relationship.objects.create(ContractUser=user4,ContractForRelationship=contract2,RelationshipType='f')
        Relationship.objects.create(ContractUser=user6,ContractForRelationship=contract2,RelationshipType='f')
        Relationship.objects.create(ContractUser=user5,ContractForRelationship=contract2,RelationshipType='c')
        
    def test_contract_permission(self):
        emperor_of_the_universe = User.objects.get(username="brian")
        josh = User.objects.get(username="josh")
        matt = User.objects.get(username="matt")
        erin = User.objects.get(username="erin")
        kenny = User.objects.get(username="kenny")
        clara = User.objects.get(username="clara")
        
        # Assert I am the overall master of this domain
        self.assertEqual(emperor_of_the_universe.is_superuser, True)
        
        contract1 = Contract.objects.get(Name="Josh Contract")
        contract2 = Contract.objects.get(Name="Erin Contract")
        
        # Check super user permissions
        self.assertIsNotNone(contract1.does_this_user_have_permission_to_see_contract(emperor_of_the_universe))
        self.assertIsNotNone(contract2.does_this_user_have_permission_to_see_contract(emperor_of_the_universe))
        
        # Assert all contract 1 permissions
        self.assertIsNotNone(contract1.does_this_user_have_permission_to_see_contract(josh))
        self.assertIsNotNone(contract1.does_this_user_have_permission_to_see_contract(matt))
        self.assertIsNone(contract1.does_this_user_have_permission_to_see_contract(erin))
        self.assertIsNone(contract1.does_this_user_have_permission_to_see_contract(clara))
        self.assertIsNone(contract1.does_this_user_have_permission_to_see_contract(kenny))
        
        # Assert all contract 2 permissions
        self.assertIsNotNone(contract2.does_this_user_have_permission_to_see_contract(erin))
        self.assertIsNotNone(contract2.does_this_user_have_permission_to_see_contract(kenny))
        self.assertIsNotNone(contract2.does_this_user_have_permission_to_see_contract(clara))
        self.assertIsNone(contract2.does_this_user_have_permission_to_see_contract(josh))
        self.assertIsNone(contract2.does_this_user_have_permission_to_see_contract(matt))

class ContractCreationScreenTest(TestCase):
    def setUp(self):
        timezone.activate(pytz.timezone("America/New_York"))
        
        # Users
        brian = User.objects.create(username="Brian@workinflow.co",email="Brian@workinflow.co",first_name="Brian",last_name="Katchmar")
        brian.set_password("Th3L10nK1ng15Fun")
        brian.save()
        
        kenny = User.objects.create(username="Kenny@workinflow.co",email="Kenny@workinflow.co",first_name="Kenny",last_name="Kim") # Has User Settings, has associated types, neither of the two fields we check
        kenny.set_password("Thing5Ar3Gr34t")
        kenny.save()
        
        clara = User.objects.create(username="Clara@workinflow.co",email="Clara@workinflow.co",first_name="Clara",last_name="Chang")
        clara.set_password("Thing5Ar3Gr34t")
        clara.save()
        
        overlord = User.objects.create(username="Overlord@workinflow.co",email="Overlord@workinflow.co",first_name="Mister",last_name="Universe",is_superuser=True)
        overlord.set_password("irule")
        overlord.save()
        
        if not Contract.objects.filter(Name="Brian Contract 1").exists():
            contract_1 = Contract.objects.create(Creator=brian,Name="Brian Contract 1",StartDate=date.today(),EndDate=date.today())
            Relationship.objects.create(ContractUser=brian,ContractForRelationship=contract_1,RelationshipType='f')
    
    def testCurrentContractNotBeingEditted(self):
        c = Client()
        loginAttempt = c.login(username='Brian@workinflow.co', password='Th3L10nK1ng15Fun')
        response = c.get("/inflow/projects/contract/create")
        
        self.assertEqual(response.context["contract_info"]["id"], 0)
        self.assertEqual(200,response.status_code) # User can see the page
        
    def testFirstScreenEditOk(self):
        contract_1 = Contract.objects.get(Name="Brian Contract 1")
        request_url = ("/inflow/projects/contract/edit/%s" % contract_1.id)
        
        c = Client()
        loginAttempt = c.login(username="Brian@workinflow.co", password="Th3L10nK1ng15Fun")
        response = c.get(request_url)
        
        self.assertEqual(response.context["contract_info"]["id"], contract_1.id)
        self.assertEqual(response.context["contract_info"]["contract_name"], contract_1.Name)
        self.assertEqual(200,response.status_code)
        
    def testFirstScreenEditKickedOutKenny(self):
        contract_1 = Contract.objects.get(Name="Brian Contract 1")
        request_url = ("/inflow/projects/contract/edit/%s" % contract_1.id)
        
        c = Client()
        loginAttempt = c.login(username='Kenny@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.get(request_url)
        
        self.assertEqual(200,response.status_code) # User got a 404
        self.assertFalse("contract_info" in response.context)
    
    def testSuperUserCanSeeContract(self):
        contract_1 = Contract.objects.get(Name="Brian Contract 1")
        request_url = ("/inflow/projects/contract/edit/%s" % contract_1.id)
        
        c = Client()
        loginAttempt = c.login(username="Overlord@workinflow.co", password="irule")
        response = c.get(request_url)
        
        self.assertEqual(200,response.status_code) # User got a 404
        self.assertTrue("contract_info" in response.context)
        
    def testContractBeingCreatedAfterPostFromScreenOne(self):
        number_of_current_contracts = len(Contract.objects.all())
        create_url = "/inflow/projects/contract/create"
        
        c = Client()
        loginAttempt = c.login(username='Kenny@workinflow.co', password='Thing5Ar3Gr34t')
        response = c.post(create_url, 
                          { 
                              "contractName" : "Next Attempt to Create A Contract", 
                              "contract-type" : "milestones", 
                              "description" : "", 
                              "who-owns" : "myself",
                              "company-name" : "Generic Company Name",
                              "companyBillingName" : "A Billing Name",
                              "companyContactEmail" : "Email@email.net",
                              "action" : "Continue"
                           })
        
        number_of_current_contracts_2 = len(Contract.objects.all())
        
        self.assertTrue(loginAttempt)
        self.assertEqual(302,response.status_code)
        self.assertNotEqual(number_of_current_contracts, number_of_current_contracts_2)
    
    def testContractCanBeEditInScreen2(self):
        contract_name = "Brian Contract 1"
        contract_1 = Contract.objects.get(Name=contract_name)
        request_url = ("/inflow/projects/contract/create/step-2/%s" % contract_1.id)
        
        c = Client()
        loginAttempt = c.login(username="Brian@workinflow.co", password="Th3L10nK1ng15Fun")
        response = c.post(request_url, 
                          { 
                              "contractStartDate" : "Jul 30 2018", 
                              "contractEndDate" : "Jul 31 2018", 
                              "hourlyRate" : "0",
                              "downPaymentAmount" : "0",
                              "totalNumberOfRevisions": "3",
                              "milestoneName" : ["MS1", "MS2"],
                              "milestoneDescription" : ["", ""],
                              "milestonesEstimateHours" : ["0", "0"],
                              "milestoneAmount" : ["150", "200"],
                              "milestoneDeadline" : ["Jul 30 2018", " Jul 30 2018"],
                              "milestoneId" : ["0", "0"],
                              "removeMilestone" : ["false", "false"],
                              "totalContractAmount" : "350",
                              "downPaymentAmount" : "0",
                              "action" : "Continue"
                           })
        
        self.assertTrue(loginAttempt)
        
        contract_edited = Contract.objects.get(Name=contract_name)
        contract_edited_milestones = Milestone.objects.filter(MilestoneContract=contract_edited)
        
        self.assertEqual(contract_edited.StartDate, date(2018,7,30))
        self.assertEqual(contract_edited.EndDate, date(2018,7,31))
        self.assertNotEqual(contract_edited.StartDate, date(2018,8,1))
        self.assertEqual(len(contract_edited_milestones), 2)

class ContractParagraphTest(TestCase):
    def setUp(self):
        timezone.activate(pytz.timezone("America/New_York"))
        
        # Users
        brian = User.objects.create(username="Brian@workinflow.co",email="Brian@workinflow.co",first_name="Brian",last_name="Katchmar")
        brian.set_password("Th3L10nK1ng15Fun")
        brian.save()
        
        kenny = User.objects.create(username="Kenny@workinflow.co",email="Kenny@workinflow.co",first_name="Kenny",last_name="Kim") # Has User Settings, has associated types, neither of the two fields we check
        kenny.set_password("Thing5Ar3Gr34t")
        kenny.save()
        
        clara = User.objects.create(username="Clara@workinflow.co",email="Clara@workinflow.co",first_name="Clara",last_name="Chang")
        clara.set_password("Thing5Ar3Gr34t")
        clara.save()
        
        if not Contract.objects.filter(Name="Kenny Contract 1").exists():
            contract_1 = Contract.objects.create(Creator=kenny,Name="Kenny Contract 1",StartDate=date.today(),EndDate=date.today())
            Relationship.objects.create(ContractUser=kenny,ContractForRelationship=contract_1,RelationshipType='f')
            ContractText.objects.create(ContractFor=contract_1,Order=1,ParagraphText='The Legend of Bucket-Head Man')
        
        if not Contract.objects.filter(Name="Clara Contract 1").exists():
            contract_2 = Contract.objects.create(Creator=clara,Name="Clara Contract 1",StartDate=date.today(),EndDate=date.today())
            Relationship.objects.create(ContractUser=clara,ContractForRelationship=contract_1,RelationshipType='f')
            
    def testContractParagraphsCount(self):
        contract_1 = Contract.objects.get(Name="Kenny Contract 1")
        contract_1_paras = contract_1.get_contract_text()
        
        contract_2 = Contract.objects.get(Name="Clara Contract 1")
        contract_2_paras = contract_2.get_contract_text()
        
        self.assertEqual(1,len(contract_1_paras)) # We only put 1 in
        self.assertEqual(4,len(contract_2_paras)) # Default

class ContractPhoneNumberTest(TestCase):
    test_contract_name = "Phone Number Error Test"
    
    def setUp(self):
        usd = Currency.objects.create()
        
        USA = Country()
        USA.PrimaryCurrency = usd
        USA.Name = "United States"
        USA.Code = "US"
        USA.save()
        
        brianUser = User.objects.create(
                            username="brian@workinflow.co",
                            email="brian@workinflow.co",
                            first_name="Brian",
                            last_name="Katchmar",
                            is_staff=False,
                            is_active=True,
                            is_superuser=False)
        
        brianUser.set_password("ilikechickenfingersandpizza")
        brianUser.save()
        
        if not Contract.objects.filter(Name=self.test_contract_name).exists():
            contract_1 = Contract.objects.create(Creator=brianUser,Name=self.test_contract_name,StartDate=date.today(),EndDate=date.today())
            contract_1.create_slug()
            contract_1.save()
            
            Relationship.objects.create(ContractUser=brianUser,ContractForRelationship=contract_1,RelationshipType='f')
            Recipient.objects.create(ContractForRecipient=contract_1,Name="Snickity Snack",BillingName="Billing Things INC",PhoneNumber="1243",EmailAddress="email@email.com")
            
    def testBogusPhoneNumberContractCreationStepOneTest(self):
        contract_1 = Contract.objects.get(Name=self.test_contract_name)
        url = ("/inflow/projects/contract/edit/%s" % contract_1.id)
        
        c = Client()
        loginAttempt = c.login(username="brian@workinflow.co", password='ilikechickenfingersandpizza')
        response = c.get(url)
        
        self.assertTrue(loginAttempt)
        self.assertEqual(200,response.status_code) # User can see the page
        self.assertEqual(contract_1.id,response.context["contract_info"]["id"])
    
    def testBogusPhoneNumberContractCreationStepFourTest(self):
        contract_1 = Contract.objects.get(Name=self.test_contract_name)
        url = ("/inflow/projects/contract/create/step-4/%s" % contract_1.id)
        
        c = Client()
        loginAttempt = c.login(username="brian@workinflow.co", password='ilikechickenfingersandpizza')
        response = c.get(url)
        
        self.assertTrue(loginAttempt)
        self.assertEqual(200,response.status_code) # User can see the page
        self.assertEqual(contract_1.id,response.context["contract_info"].id)