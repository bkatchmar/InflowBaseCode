from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView

import base64, mimetypes
import boto3
import urllib.request
from PIL import Image

# Error Pages
def server_error(request):
    return render(request, "errors/500.html")
 
def not_found(request):
    return render(request, "errors/404.html")

class DemoLoginView(TemplateView):
    template_name = "demologin.html"

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
    
class FreelancerActiveUseLoFiHome(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.home.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiQuickView(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.quick-view.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectMilestone(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectMilestoneUploadIdle(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.upload-idle.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectMilestoneUploadProgress(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.upload-progress.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectOverview(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.overview.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectInvoices(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.invoices.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectFiles(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.files.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectMilestonePreview(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.preview.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectMilestonePreviewNote(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.preview.note.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)    

class FreelancerActiveUseLoFiSpecificProjectMilestoneScheduleDelivery(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.schedule-delivery.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class FreelancerActiveUseLoFiSpecificProjectMilestoneScheduleDeliveryConfirmSend(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.schedule-delivery.confirm-send.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class FreelancerActiveUseLoFiSpecificProjectMilestoneScheduleDeliveryConfirmSendNow(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.milestones.schedule-delivery.confirm-send-now.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class FreelancerActiveUseLoFiSpecificProjectEmailConfirmFreelancer(TemplateView):
    template_name = "freelancer_active_flow_lofi/email.confirm.freelancer.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class FreelancerActiveUseLoFiSpecificProjectEmailConfirmClient(TemplateView):
    template_name = "freelancer_active_flow_lofi/email.confirm.client.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
    
class ClientActiveUseLoFiHome(TemplateView):
    template_name = "client_active_flow_lofi/client.home.dashboard.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : True }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : True }
        return render(request, self.template_name, context)
    
class ClientActiveUseLoFiProjectsHome(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.home.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)
    
class ClientActiveUseLoFiQuickView(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.quick-view.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

class ClientActiveUseLoFiSpecificProjectMilestone(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.specific-project.milestones.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

class ClientActiveUseLoFiSpecificProjectOverview(TemplateView):
    template_name = "freelancer_active_flow_lofi/projects.dashboard.specific-project.overview.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)
    
class ClientActiveUseLoFiSpecificProjectInvoices(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.specific-project.invoices.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)
    
class ClientActiveUseLoFiSpecificProjectFiles(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.specific-project.files.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)
    
class ClientActiveUseLoFiSpecificProjectMilestonePreview(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.specific-project.milestones.preview.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

class ClientActiveUseLoFiSpecificProjectMilestonePreviewDecline(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.specific-project.milestones.preview.decline.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)
    
class ClientActiveUseLoFiSpecificProjectMilestonePreviewDeclineSend(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.specific-project.milestones.preview.decline.send.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

class ClientActiveUseLoFiSpecificProjectMilestoneAccept(TemplateView):
    template_name = "client_active_flow_lofi/projects.dashboard.specific-project.milestones.accept.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

class ClientActiveUseLoFiSpecificProjectMilestoneAcceptConfirmSend(TemplateView):
    template_name = "client_active_flow_lofi/projects.accept.confirm.send.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

class CreateContractStepOneDemo(TemplateView):
    template_name = "contract_creation/create.contract.step-1.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)