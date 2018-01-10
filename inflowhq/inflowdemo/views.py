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