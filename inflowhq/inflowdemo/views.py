from django.shortcuts import render
from django.views.generic import TemplateView

class DemoLoginView(TemplateView):
    template_name = "demologin.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
class DemoLoginGmailOverlayView(TemplateView):
    template_name = "gmal-overlay.html"
    
    def get(self, request):
        return render(request, self.template_name)