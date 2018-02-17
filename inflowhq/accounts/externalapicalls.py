from django.conf import settings
import requests

class LinkedInApi():
    clientid = settings.LINKEDIN_CLIENT_ID
    clientsecret = settings.LINKEDIN_CLIENT_SECRET
    callstate = settings.LINKEDIN_CALL_STATE
    redirecturl = settings.LINKEDIN_REDIRECT_URL
    
    def request_authorization_token(self,authtokencode):
        posturl = 'https://www.linkedin.com/oauth/v2/accessToken' # Set destination URL here
        post_fields = {
                       'grant_type': 'authorization_code',
                       'code':authtokencode,
                       'redirect_uri':self.redirecturl,
                       'client_id':self.clientid,
                       'client_secret':self.clientsecret
        }
        stripeResp = requests.post(posturl, params=post_fields)
        json = stripeResp.json()
        return json
    
    def get_basic_profile_info(self,oauthtoken):
        infourl = "https://api.linkedin.com/v1/people/~:(id,firstName,headline,lastName,picture-url,email-address)?format=json" # Set destination URL here
        headers = {"Connection":"Keep-Alive","Authorization":"Bearer %s" % oauthtoken}
        r = requests.get(infourl, headers=headers)
        
        if r.status_code == 401:
            return {"LinkedInError":True,"LinkedInErrorMessage":"The Authorization Token Is No Longer Valid"}
        else:
            return r.json()
        
class GoogleApi():
    def validate_google_token(self,token_value):
        post_url = "https://www.googleapis.com/oauth2/v3/tokeninfo" # Set destination URL here
        post_fields = { "id_token": token_value }
        google_resp = requests.post(post_url, params=post_fields)
        json_resp = google_resp.json()
        
        if google_resp.status_code == 200:
            json_resp["response_ok"] = True
            if json_resp["email_verified"] is None:
                json_resp["email_verified"] = False
        else:
            json_resp["response_ok"] = False
            
        return json_resp