from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.linkedincalls import LinkedInApi
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
        
        if usersettings.LinkedInAccessToken is not None:
            if usersettings.LinkedInAccessToken != "":
                apiCaller = LinkedInApi()
                apiLinkeIinInfo = apiCaller.GetBasicProfileInfo(usersettings.LinkedInAccessToken)
                context["linkedininfo"] = apiLinkeIinInfo
        
        return render(request, self.template_name, context)