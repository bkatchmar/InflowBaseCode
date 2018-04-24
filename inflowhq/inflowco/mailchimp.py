from django.conf import settings
import requests

class MailChimpCommunication():
    mailchimp_region = settings.MAILCHIMP_REGION
    mailchimp_username = settings.MAILCHIMP_USERNAME
    mailchimp_api_key = settings.MAILCHIMP_API_KEY
    
    def post_email_to_list(self,list_id,email):
        post_url_list_details = ("https://%s.api.mailchimp.com/3.0/lists/%s/members" % (self.mailchimp_region, list_id))
        post_fields_list_details = {
            "email_address" : email,
            "email_type" : "html",
            "status" : "subscribed"
        }
        post_headers = {"content-type":"application/json"}
        response_post = requests.post(post_url_list_details, auth=(self.mailchimp_username, self.mailchimp_api_key), headers=post_headers, json=post_fields_list_details)
        response_post_json = response_post.json()