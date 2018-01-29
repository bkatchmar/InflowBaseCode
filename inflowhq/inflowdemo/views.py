from django.shortcuts import render
from django.views.generic import TemplateView

import base64, urllib.request, mimetypes

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

class DemoCreateContractReceivedEmail(TemplateView):
    template_name = "receivedemail.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoCreateContractClientEmailSigned(TemplateView):
    template_name = "clientemailsigned.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoCreateContractClientEmailRevision(TemplateView):
    template_name = "clientemailrevision.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoCreateContractFreelanceEmailSigned(TemplateView):
    template_name = "freelanceemailsigned.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoCreateContractFreelanceEmailRevision(TemplateView):
    template_name = "freelanceemailrevision.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoWelcome(TemplateView):
    template_name = "welcome.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoAddress(TemplateView):
    template_name = "address.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoCongratulation(TemplateView):
    template_name = "congratulations.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class DemoStripeConnect(TemplateView):
    template_name = "stripe.connect.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class DemoStripeThanks(TemplateView):
    template_name = "stripe.thanks.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class DemoTermsOfUse(TemplateView):
    template_name = "accept.terms-of-use.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class DemoProjectDetails(TemplateView):
    template_name = "project.details.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class DemoUploadMilestone(TemplateView):
    template_name = "project.upload.milestone.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class DemoPreviewMilestone(TemplateView):
    template_name = "project.preview.milestone.html"

    def get_context_data(self, **kwargs):
        path = "https://www.fuzzyduk.com/wp-content/uploads/2017/04/MIN01WH.jpg"
        mime = mimetypes.guess_type(path)
        image = urllib.request.urlopen(path)
        image_64 = base64.encodestring(image.read())
        
        # Call the base implementation first to get a context
        context = super(DemoPreviewMilestone, self).get_context_data(**kwargs)
        context["imgData"] = u'data:%s;base64,%s' % (mime[0], str(image_64,"utf-8").replace("\n", ""))
        return context