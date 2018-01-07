from django.shortcuts import render
from django.views.generic import TemplateView

class DemoLoginView(TemplateView):
    template_name = "demologin.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        return render(request, self.template_name)
    
class DemoMyProjectsScreen(TemplateView):
    template_name = "myprojects.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        return render(request, self.template_name)
    
class DemoCreateNewContract(TemplateView):
    template_name = "createcontract.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        return render(request, self.template_name)
    
class DemoCreateContractClient(TemplateView):
    template_name = "contract.creation.confirm.client.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        return render(request, self.template_name)
    
class DemoCreateContractFreelancer(TemplateView):
    template_name = "contract.creation.confirm.freelancer.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        return render(request, self.template_name)
    
class DemoAmendContract(TemplateView):
    template_name = "amendcontract.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        return render(request, self.template_name)