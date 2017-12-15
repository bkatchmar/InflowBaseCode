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
        print(self.template_name)
        print("I need to print this to see if this will even work here")
        return render(request, self.template_name)
    
    def post(self, request):
        print(self.template_name)
        print("I need to print this to see if this will even work here")
        return render(request, self.template_name)