from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from inflowco.models import Currency

class LoginView(TemplateView):
    template_name = 'login.html'
    
    def get(self, request):
        context = {'message':''}
        return render(request, 'login.html', context)
    
    def post(self, request):
        context = {'message':''}
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/inflow/currencies/')
        
        return render(request, 'login.html', context)
    
class CurrencyListView(LoginRequiredMixin, TemplateView):
    template_name = 'listcurrencies.html'
    
    def get_queryset(self):
        return Currency.objects.all()
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CurrencyListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the currencies
        context['currencies'] = self.get_queryset()
        return context