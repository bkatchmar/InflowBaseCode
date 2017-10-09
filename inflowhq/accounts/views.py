from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.models import UserSettings

class AccountInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'viewaccountinfo.html'
    
    def get(self, request):
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user

        usersettings = usersettings.GetSettingsBasedOnUser(currentlyloggedinuser)
        context = {
                   'settings':usersettings
                   }
        return render(request, 'viewaccountinfo.html', context)