from django.shortcuts import render
from django.views.generic import TemplateView

import base64, mimetypes
import boto3
import urllib.request

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

    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        
        # Get data from the POST
        uploaded_file = request.FILES.get("deliverable", False)
        google_drive_file = request.POST.get("drive-url", "")
        dropzone_files = request.FILES.getlist("freelancer-deliverables")
        
        # If we have an actual file, time to prepare it to be uploaded to AWS
        if uploaded_file != False:
            context = {}
            deliverable_key = uploaded_file.__str__()
            amazon_destination_bucket_name = "inflow-upload-demo"
            amazon_caller_resource = boto3.resource("s3", region_name="us-east-1",aws_access_key_id="AKIAIQKGNH2YH2ZD2DOQ", aws_secret_access_key="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")
            amazon_caller_client = boto3.client("s3", region_name="us-east-1",aws_access_key_id="AKIAIQKGNH2YH2ZD2DOQ", aws_secret_access_key="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")
            
            # Determine if we have to create a new bucket
            bucket_list = amazon_caller_client.list_buckets()
            need_to_create_bucket = True
            for bucket in bucket_list["Buckets"]:
                if bucket["Name"] == amazon_destination_bucket_name:
                    need_to_create_bucket = False
            
            # If we need to create a new bucket, do so
            # TO DO: Make this a more streamlined process
            if need_to_create_bucket:
                amazon_caller_resource.create_bucket(Bucket=amazon_destination_bucket_name)

            # Place the uploaded file in Amazon
            amazon_caller_resource.Bucket(amazon_destination_bucket_name).put_object(ACL="public-read", Key=deliverable_key, Body=uploaded_file)
            
            # Finally, get the newly created URL for the image and base64 encode it
            path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_key))
            mime = mimetypes.guess_type(path)
            image = urllib.request.urlopen(path)
            image_64 = base64.encodestring(image.read())
            context["imgData"] = u'data:%s;base64,%s' % (mime[0], str(image_64,"utf-8").replace("\n", ""))
        elif google_drive_file != "":
            mime = mimetypes.guess_type(google_drive_file)
            image = urllib.request.urlopen(google_drive_file)
            image_64 = base64.encodestring(image.read())
            context["imgData"] = u'data:%s;base64,%s' % (mime[0], str(image_64,"utf-8").replace("\n", ""))
        elif len(dropzone_files) > 0:
            context = {}
            
            # Initial AWS Variables
            amazon_destination_bucket_name = "inflow-upload-demo"
            amazon_caller_resource = boto3.resource("s3", region_name="us-east-1",aws_access_key_id="AKIAIQKGNH2YH2ZD2DOQ", aws_secret_access_key="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")
            amazon_caller_client = boto3.client("s3", region_name="us-east-1",aws_access_key_id="AKIAIQKGNH2YH2ZD2DOQ", aws_secret_access_key="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")
            
            # Determine if we have to create a new bucket
            bucket_list = amazon_caller_client.list_buckets()
            need_to_create_bucket = True
            for bucket in bucket_list["Buckets"]:
                if bucket["Name"] == amazon_destination_bucket_name:
                    need_to_create_bucket = False
            
            # If we need to create a new bucket, do so
            # TO DO: Make this a more streamlined process
            if need_to_create_bucket:
                amazon_caller_resource.create_bucket(Bucket=amazon_destination_bucket_name)
            
            path = ""
            
            for dropzone_file in dropzone_files:
                deliverable_key = dropzone_file.__str__()
                
                # Place the uploaded file in Amazon
                amazon_caller_resource.Bucket(amazon_destination_bucket_name).put_object(ACL="public-read", Key=deliverable_key, Body=dropzone_file)
                path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_key))
            
            mime = mimetypes.guess_type(path)
            image = urllib.request.urlopen(path)
            image_64 = base64.encodestring(image.read())
            context["imgData"] = u'data:%s;base64,%s' % (mime[0], str(image_64,"utf-8").replace("\n", ""))
        else:
            context = self.get_context_data(request)
        
        return render(request, self.template_name, context)

    def get_context_data(self, request, **kwargs):
        path = "https://www.fuzzyduk.com/wp-content/uploads/2017/04/MIN01WH.jpg"
        mime = mimetypes.guess_type(path)
        image = urllib.request.urlopen(path)
        image_64 = base64.encodestring(image.read())
        
        # Call the base implementation first to get a context
        context = super(DemoPreviewMilestone, self).get_context_data(**kwargs)
        context["imgData"] = u'data:%s;base64,%s' % (mime[0], str(image_64,"utf-8").replace("\n", ""))
        return context

class DemoUploadMilestoneDrag(TemplateView):
    template_name = "project.upload.drag.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)