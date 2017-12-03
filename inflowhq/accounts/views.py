from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.externalapicalls import LinkedInApi
from accounts.models import UserLinkedInInformation, UserSettings

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
        
        userLinkedInProfileInfo = UserLinkedInInformation.objects.filter(UserAccount=currentlyloggedinuser).first()
        if userLinkedInProfileInfo is not None:
            if userLinkedInProfileInfo.LinkedInAccessToken != "":
                apiCaller = LinkedInApi()
                apiLinkeIinInfo = apiCaller.GetBasicProfileInfo(userLinkedInProfileInfo.LinkedInAccessToken)
                context["linkedininfo"] = apiLinkeIinInfo
        
        return render(request, self.template_name, context)