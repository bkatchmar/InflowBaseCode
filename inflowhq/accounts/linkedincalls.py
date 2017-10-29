from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from accounts.models import UserSettings
import requests

class LinkedInApi():
    clientid = settings.LINKEDIN_CLIENT_ID
    clientsecret = settings.LINKEDIN_CLIENT_SECRET
    callstate = settings.LINKEDIN_CALL_STATE
    redirecturl = settings.LINKEDIN_REDIRECT_URL
    
    def RequestAuthorizationToken(self,authtokencode):
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
    
    def GetBasicProfileInfo(self,oauthtoken):
        infourl = "https://api.linkedin.com/v1/people/~:(id,firstName,headline,lastName,picture-url,email-address)?format=json" # Set destination URL here
        headers = {"Connection":"Keep-Alive","Authorization":"Bearer %s" % oauthtoken}
        r = requests.get(infourl, headers=headers)
        
        if r.status_code == 401:
            return {"LinkedInError":True,"LinkedInErrorMessage":"The Authorization Token Is No Longer Valid"}
        else:
            return r.json()