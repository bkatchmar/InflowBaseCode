from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.models import UserSettings
from contractsandprojects.models import Contract
from contractsandprojects.email_handler import EmailHandler

class ContractCreationView(LoginRequiredMixin, TemplateView):
    template_name = "projects.home.html"
    
    def get(self, request):
        context = {
            "projects" : [
                { "project_title" : "NFL Experience App", "project_client" : "National Football League", "progress" : "Completed", "start_date" : "02 JAN 2018", "end_date": "02 FEB 2018" },
                { "project_title" : "Blake Federov Book", "project_client" : "Client", "progress" : "In Progress", "start_date" : "03 MAR 2018", "end_date": "30 JUL 2018" },
                { "project_title" : "Recipe Blog Post", "project_client" : "Le Cordon Bleu", "progress" : "Not Started", "start_date" : "31 DEC 2018", "end_date": "31 DEC 2018" }
            ]
        }
        return render(request, self.template_name, context)
    
class EmailPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "email_area.html"
    
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        
        # Objects we are going to use to send our emails
        contract_to_send = Contract()
        handler = EmailHandler()
        
        email_mode = request.POST.get("mode", "")
        handler.send_base_email(contract_to_send)
        return render(request, self.template_name, context)