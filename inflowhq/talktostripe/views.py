from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from accounts.models import UserSettings
from talktostripe.stripecommunication import StripeCommunication
import stripe

class BaseTalk(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'
    
    def get(self, request):
        context = {}
        stripe.api_key = settings.STRIPE_TEST_API_SECRET
        
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user
            
        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        
        comm = StripeCommunication()
        comm.CreateNewStripeCustomerWithId(usersettings)
        
        return render(request, 'base.html', context)