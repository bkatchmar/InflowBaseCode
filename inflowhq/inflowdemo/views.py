from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

import os
import base64, mimetypes
import boto3
import requests
import urllib.request
from PIL import Image
from io import BytesIO

import httplib2
import urllib.parse
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.contrib import gce
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
import re

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
        context = {}
        
        # Get data from the POST
        uploaded_file = request.FILES.get("deliverable", False)
        google_drive_file = request.POST.get("drive-url", "")
        google_drive_file_name = request.POST.get("drive-name", "")
        dropzone_files = request.FILES.getlist("freelancer-deliverables")
        
        # Boto3 Classes
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
        amazon_s3_bucket = amazon_caller_resource.Bucket(amazon_destination_bucket_name)
        
        # If we have an actual file, time to prepare it to be uploaded to AWS
        if uploaded_file != False:
            deliverable_key = uploaded_file.__str__()
            deliverable_preview_key = ("preview/%s" % deliverable_key)
            
            if not self.does_this_file_exists_in_bucket(amazon_s3_bucket,deliverable_key):
                amazon_s3_bucket.put_object(ACL="public-read", Key=deliverable_key, Body=uploaded_file)
            
            # Finally, get the newly created URL for the image and base64 encode it
            primary_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_key))
            watermarked_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_preview_key))
            self.watermark_image_and_upload_to_s3(primary_path,watermarked_path,deliverable_preview_key,amazon_s3_bucket)
            context["preview_path"] = watermarked_path
        elif google_drive_file != "" and google_drive_file_name != "":
            deliverable_key = google_drive_file_name
            deliverable_preview_key = ("preview/%s" % deliverable_key)
            
            primary_image_response = requests.get(google_drive_file)
            primary_image = Image.open(BytesIO(primary_image_response.content))
            
            if not self.does_this_file_exists_in_bucket(amazon_s3_bucket,deliverable_key):
                amazon_s3_bucket.put_object(ACL="public-read", Key=deliverable_key, Body=primary_image_response.content)
                
            # Finally, get the newly created URL for the image and base64 encode it
            primary_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_key))
            watermarked_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_preview_key))
            self.watermark_image_and_upload_to_s3(primary_path,watermarked_path,deliverable_preview_key,amazon_s3_bucket)
            context["preview_path"] = watermarked_path
        elif len(dropzone_files) > 0:
            final_watermark_path =""
            
            for dropzone_file in dropzone_files:
                deliverable_key = dropzone_file.__str__()
                deliverable_preview_key = ("preview/%s" % deliverable_key)
                
                # Place the uploaded file in Amazon
                if not self.does_this_file_exists_in_bucket(amazon_s3_bucket,deliverable_key):
                    amazon_s3_bucket.put_object(ACL="public-read", Key=deliverable_key, Body=dropzone_file)
                
                primary_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_key))
                watermarked_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_destination_bucket_name, deliverable_preview_key))
                
                self.watermark_image_and_upload_to_s3(primary_path,watermarked_path,deliverable_preview_key,amazon_s3_bucket)
                final_watermark_path = watermarked_path
            
            context["preview_path"] = final_watermark_path
        
        return render(request, self.template_name, context)
    
    def does_this_file_exists_in_bucket(self,bucket,key_name):
        for object in bucket.objects.all():
            if object.key == key_name:
                return True
        
        return False
    
    def watermark_image_and_upload_to_s3(self,image_path,watermarked_image_path,preview_key,amazon_bucket):
        primary_image_path = image_path
        watermark_image_path = "https://s3.us-east-2.amazonaws.com/inflowcssjs/img/inflow_watermark.png"
        
        primary_image_response = requests.get(primary_image_path)
        watermark_image_response = requests.get(watermark_image_path)
        
        primary_image = Image.open(BytesIO(primary_image_response.content))
        watermark_image = Image.open(BytesIO(watermark_image_response.content))
        
        watermark_image_resized = watermark_image.resize((primary_image.width, primary_image.height))
        
        primary_image_copy = primary_image.copy()
        
        position = (0, 0)
        primary_image_copy.paste(watermark_image_resized, position, watermark_image_resized)
        
        imgByteArr = BytesIO()
        primary_image_copy.save(imgByteArr, format="JPEG")
        imgByteArr.seek(0)  # Without this line it fails
        
        if not self.does_this_file_exists_in_bucket(amazon_bucket,preview_key):
            amazon_bucket.put_object(ACL="public-read", Key=preview_key, Body=imgByteArr)

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
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        action = request.POST.get("action", "")
        contract_type = request.POST.get("contract-type", "milestones")
        
        if action == "Continue":
            if contract_type == "milestones":
                return redirect(reverse("htmldemos:contract_creation_lump_sum"))
            else:
                return redirect(reverse("htmldemos:contract_creation_hourly"))
        else:
            return redirect(reverse("htmldemos:freelancer_active_use"))
        
        return render(request, self.template_name, context)
    
class CreateContractStepTwoLumpSum(TemplateView):
    template_name = "contract_creation/create.contract.step-2.lump-sum.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        action = request.POST.get("action", "")
        contract_type = request.POST.get("contract-type", "milestones")
        
        if action == "Continue":
            return redirect(reverse("htmldemos:contract_creation_extra_fees"))
        else:
            return redirect(reverse("htmldemos:contract_creation"))
        
        return render(request, self.template_name, context)

class CreateContractStepTwoHourly(TemplateView):
    template_name = "contract_creation/create.contract.step-2.hourly.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        action = request.POST.get("action", "")
        contract_type = request.POST.get("contract-type", "milestones")
        
        if action == "Continue":
            return redirect(reverse("htmldemos:contract_creation_extra_fees"))
        else:
            return redirect(reverse("htmldemos:contract_creation"))
        
        return render(request, self.template_name, context)

class CreateContractStepThreeHourly(TemplateView):
    template_name = "contract_creation/create.contract.step-3.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        referer_mode = "lump-sum"
        
        referer = request.META.get('HTTP_REFERER')
        if not referer:
            referer_mode = "lump-sum"
            context["contract_mode"] = referer_mode
            return render(request, self.template_name, context)

        # remove the protocol and split the url at the slashes
        referer = re.sub('^https?:\/\/', '', referer).split('/')
        referer_mode = referer[len(referer)-1]
        
        # add the slash at the relative path's view and finished
        referer = u'/' + u'/'.join(referer[1:])
        
        context["contract_mode"] = referer_mode
        
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        action = request.POST.get("action", "")
        mode = request.POST.get("mode", "milestones")
        
        if action == "Continue":
            if mode == "lump-sum":
                return redirect(reverse("htmldemos:contract_overview_lump_sum"))
            else:
                return redirect(reverse("htmldemos:contract_overview_hourly"))
        else:
            if mode == "lump-sum":
                return redirect(reverse("htmldemos:contract_creation_lump_sum"))
            else:
                return redirect(reverse("htmldemos:contract_creation_hourly"))
        
        return render(request, self.template_name, context)

class CreateContractStepFourLumpSum(TemplateView):
    template_name = "contract_creation/create.contract.step-4.lump-sum.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        action = request.POST.get("action", "")
        contract_type = request.POST.get("contract-type", "milestones")
        
        if action == "Continue":
            return redirect(reverse("htmldemos:contract_overview_preview_send"))
        else:
            return redirect(reverse("htmldemos:contract_creation_extra_fees"))
        
        return render(request, self.template_name, context)

class CreateContractStepFourHourly(TemplateView):
    template_name = "contract_creation/create.contract.step-4.hourly.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        action = request.POST.get("action", "")
        
        if action == "Continue":
            return redirect(reverse("htmldemos:contract_overview_preview_send"))
        else:
            return redirect(reverse("htmldemos:contract_creation_extra_fees"))
        
        return render(request, self.template_name, context)

class CreateContractStepFourLumpSumEdit(TemplateView):
    template_name = "contract_creation/create.contract.step-4.lump-sum.edit.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)    

class CreateContractStepFourHourlyEdit(TemplateView):
    template_name = "contract_creation/create.contract.step-4.hourly.edit.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)
    
class CreateContractStepFive(TemplateView):
    template_name = "contract_creation/create.contract.step-5.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        referer_mode = "lump-sum"
        
        referer = request.META.get('HTTP_REFERER')
        if not referer:
            referer_mode = "lump-sum"
            context["contract_mode"] = referer_mode
            return render(request, self.template_name, context)

        # remove the protocol and split the url at the slashes
        referer = re.sub('^https?:\/\/', '', referer).split('/')
        referer_mode = referer[len(referer)-1]
        
        # add the slash at the relative path's view and finished
        referer = u'/' + u'/'.join(referer[1:])
        
        context["contract_mode"] = referer_mode
        
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        
        action = request.POST.get("action", "")
        mode = request.POST.get("mode", "lump-sum")
        
        if action == "Continue":
            return redirect(reverse("htmldemos:contract_overview_final"))
        else:
            if mode == "lump-sum":
                return redirect(reverse("htmldemos:contract_overview_lump_sum"))
            else:
                return redirect(reverse("htmldemos:contract_overview_hourly"))
        
        return render(request, self.template_name, context)
    
class CreateContractCongrats(TemplateView):
    template_name = "contract_creation/congrats.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

class ReviewMakingEdit(TemplateView):
    template_name = "contract_creation/review.making.edit.html"

    def get(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)

    def post(self, request):
        context = { "is_client" : True, "exclude_arrow" : False }
        return render(request, self.template_name, context)