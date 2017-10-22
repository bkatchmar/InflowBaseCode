from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from accounts.models import UserSettings
import stripe

class StripeCommunication():
    apiKey = settings.STRIPE_TEST_API_SECRET
    
    def CreateNewStripeCustomerWithId(self,userInformation,**testargs):
        if (isinstance(userInformation,UserSettings) and (userInformation.StripeApiCustomerKey is None or not userInformation.StripeApiCustomerKey)):
            try:
                stripe.api_key = self.apiKey
                
                if (testargs.get("fromtestcase")):
                    formeta = {"Joined On" : ("%s" % userInformation.Joined),"From Test Case":"Yes"}
                else:
                    formeta = {"Joined On" : ("%s" % userInformation.Joined)}
                
                createdStripeUser = stripe.Customer.create(
                                       description="Inflow Customer %s" % userInformation.UserAccount.username,
                                       email=userInformation.UserAccount.email,
                                       metadata=formeta)
                
                userInformation.StripeApiCustomerKey = createdStripeUser["id"]
                userInformation.save()
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                pass
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                pass
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                pass
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                pass
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                pass
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                pass
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                pass
            
            # TO DO - Find a way to alert us a problem happened
            
    def CreateNewStripeCustomAccount(self,userInformation,**testargs):
        if (isinstance(userInformation,UserSettings) and (userInformation.StripeConnectAccountKey is None or not userInformation.StripeConnectAccountKey)):
            try:
                stripe.api_key = self.apiKey
                
                if (testargs.get("fromtestcase")):
                    formeta = {"Joined On" : ("%s" % userInformation.Joined),"Inflow Customer":userInformation.UserAccount.username,"From Test Case":"Yes"}
                else:
                    formeta = {"Joined On" : ("%s" % userInformation.Joined),"Inflow Customer":userInformation.UserAccount.username}
                
                createdStripeAccount = stripe.Account.create(
                                                               country=userInformation.BaseCountry.Code,
                                                               type="custom",
                                                               email=userInformation.UserAccount.email,
                                                               metadata=formeta
                                                               )
                
                createdStripeAccount.legal_entity.first_name = userInformation.UserAccount.first_name
                createdStripeAccount.legal_entity.last_name = userInformation.UserAccount.last_name
                createdStripeAccount.save()
                
                userInformation.StripeConnectAccountKey = createdStripeAccount["id"]
                userInformation.save()
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                pass
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                pass
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                pass
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                pass
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                pass
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                pass
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                pass
            
        # TO DO - Find a way to alert us a problem happened