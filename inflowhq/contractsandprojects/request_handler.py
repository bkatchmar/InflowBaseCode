import boto3
import datetime
import pathlib
import requests
from PIL import Image
from io import BytesIO
# Django References
from django.contrib.auth.models import User
from django.conf import settings
# Contracts and Projects App References
from contractsandprojects.models import Milestone, MilestoneFile

class RequestInputHandler():
    def get_entry_for_float(self,floatAmt):
        try:
            return float(floatAmt)
        except Exception as e:
            return 0.0
        
    def get_entry_for_int(self,int_amt):
        try:
            return int(int_amt)
        except Exception as e:
            return 0
        
    def get_entry_for_date(self,date_val):
        try:
            return datetime.datetime.strptime(date_val, "%b %d %Y")
        except Exception as e:
            return datetime.date.today()

class AmazonBotoHandler():
    def standard_file_upload(self, request_user, target_milestone, deliverable_key, uploaded_file, contract_slug, contract_id):
        amazon_bucket = self.generate_s3_bucket(request_user)
        deliverable_full_key = ("%s-%s/%s/%s" % (contract_slug, contract_id, target_milestone, deliverable_key))
        deliverable_preview_key = ("%s-%s/%s/preview/%s" % (contract_slug, contract_id, target_milestone, deliverable_key))
        
        if not self.does_this_file_exists_in_bucket(amazon_bucket,deliverable_full_key):
            amazon_bucket.put_object(ACL="public-read", Key=deliverable_full_key, Body=uploaded_file)
        else:
            # Make the file public read so we can update it
            self.find_file_in_bucket_and_set_acl(amazon_bucket, deliverable_full_key, "public-read")
            
        # Finally, get the newly created URL for the image and base64 encode it
        primary_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_bucket.name, deliverable_full_key))
        watermarked_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_bucket.name, deliverable_preview_key))
        self.watermark_image_and_upload_to_s3(primary_path, watermarked_path, deliverable_preview_key, amazon_bucket, pathlib.Path(deliverable_key).suffix)
        
        # Update the DB
        selected_milestone = Milestone.objects.get(IdMilestone=target_milestone)
        selected_milestone.MilestoneState = "p" # Set the state to In progress
        selected_milestone.save()
        
        if not MilestoneFile.objects.filter(MilestoneForFile=selected_milestone, FileName=deliverable_key).exists():
            MilestoneFile.objects.create(MilestoneForFile=selected_milestone, 
                                     FileName=deliverable_key,
                                     FileURL=primary_path,
                                     FilePreviewURL=watermarked_path,
                                     FileExtension=pathlib.Path(primary_path).suffix)
        
        # Set the primary file at this point to be private now we don't need to read from it
        self.find_file_in_bucket_and_set_acl(amazon_bucket, deliverable_full_key, "private")
    
    def google_drive_file_upload(self, request_user, target_milestone, deliverable_key, contract_slug, contract_id, google_drive_full_file):
        amazon_bucket = self.generate_s3_bucket(request_user)
        deliverable_full_key = ("%s-%s/%s/%s" % (contract_slug, contract_id, target_milestone, deliverable_key))
        deliverable_preview_key = ("%s-%s/%s/preview/%s" % (contract_slug, contract_id, target_milestone, deliverable_key))
        
        primary_image_response = requests.get(google_drive_full_file)
        primary_image = Image.open(BytesIO(primary_image_response.content))
        
        if not self.does_this_file_exists_in_bucket(amazon_bucket,deliverable_full_key):
            amazon_bucket.put_object(ACL="public-read", Key=deliverable_full_key, Body=primary_image_response.content)
        else:
            self.find_file_in_bucket_and_set_acl(amazon_bucket, deliverable_full_key, "public-read")
            
        # Finally, get the newly created URL for the image and base64 encode it
        primary_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_bucket.name, deliverable_full_key))
        watermarked_path = ("https://s3.amazonaws.com/%s/%s" % (amazon_bucket.name, deliverable_preview_key))
        self.watermark_image_and_upload_to_s3(primary_path, watermarked_path, deliverable_preview_key, amazon_bucket, pathlib.Path(deliverable_key).suffix)
        
        # Update the DB
        selected_milestone = Milestone.objects.get(IdMilestone=target_milestone)
        selected_milestone.MilestoneState = "p" # Set the state to In progress
        selected_milestone.save()
        
        if not MilestoneFile.objects.filter(MilestoneForFile=selected_milestone, FileName=deliverable_key).exists():
            MilestoneFile.objects.create(MilestoneForFile=selected_milestone, 
                                     FileName=deliverable_key,
                                     FileURL=primary_path,
                                     FilePreviewURL=watermarked_path,
                                     FileExtension=pathlib.Path(primary_path).suffix)
        
        # Set the primary file at this point to be private now we don't need to read from it
        self.find_file_in_bucket_and_set_acl(amazon_bucket, deliverable_full_key, "private")
    
    def generate_s3_bucket(self,request_user):
        # Boto3 Classes
        amazon_destination_bucket_name = ("inflow-bucket-user-%s" % request_user.id)
        amazon_caller_resource = boto3.resource("s3", region_name=settings.AWS_S3_REGION,aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        amazon_caller_client = boto3.client("s3", region_name=settings.AWS_S3_REGION,aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        
        # Determine if we have to create a new bucket
        bucket_list = amazon_caller_client.list_buckets()
        need_to_create_bucket = True
        for bucket in bucket_list["Buckets"]:
            if bucket["Name"] == amazon_destination_bucket_name:
                need_to_create_bucket = False
        
        # If we need to create a new bucket, do so
        if need_to_create_bucket:
            amazon_caller_resource.create_bucket(Bucket=amazon_destination_bucket_name)
        
        # Place the uploaded file in Amazon
        amazon_s3_bucket = amazon_caller_resource.Bucket(amazon_destination_bucket_name)
        return amazon_s3_bucket
    
    def does_this_file_exists_in_bucket(self,bucket,key_name):
        for object in bucket.objects.all():
            if object.key == key_name:
                return True
    
    def watermark_image_and_upload_to_s3(self, image_path, watermarked_image_path, preview_key, amazon_bucket, file_extension):
        file_extension = file_extension[1:].upper()
        
        if file_extension == "JPG":
            file_extension = "JPEG"
        
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
        primary_image_copy.save(imgByteArr, format=file_extension)
        imgByteArr.seek(0)  # Without this line it fails
        
        if not self.does_this_file_exists_in_bucket(amazon_bucket,preview_key):
            amazon_bucket.put_object(ACL="public-read", Key=preview_key, Body=imgByteArr)
    
    def find_file_in_bucket_and_set_acl(self,bucket,deliverable_full_key,acl_level):
        for object in bucket.objects.all():
            if object.key == deliverable_full_key:
                object.Acl().put(ACL=acl_level)