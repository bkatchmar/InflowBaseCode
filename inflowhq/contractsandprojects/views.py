from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.models import UserSettings

class ContractCreationView(LoginRequiredMixin, TemplateView):
    template_name = 'start.html'
    
    def get(self, request):
        currentlyloggedinuser = ""
        usersettings = UserSettings()
        
        if request.user.is_authenticated:
            currentlyloggedinuser = request.user

        context = {}
        return render(request, 'start.html', context)