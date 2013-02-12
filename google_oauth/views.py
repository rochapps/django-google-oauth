import os
import logging
import httplib2
import json

from oauth2client import xsrfutil
from oauth2client.django_orm import Storage
from oauth2client.client import OAuth2WebServerFlow

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import View

from google_oauth.models import Credentials, Flow


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
            Only authenticated users can proceed
        """
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)
        

class AuthCredentials(LoginRequiredMixin, View):
    """
        AuthCredentials checks to see if the user already has valid credentials
        or redirects it to google sign in page.
    """
    _flow = None
        
    def get(self, request, *args, **kwargs):
        """
        
        """
        if self.validate_credentials():
            success_url = getattr(settings, 'GCAL_SUCCESS_URL', '/')
            return HttpResponseRedirect(success_url)
        self.save_flow()
        return HttpResponseRedirect(self.get_authorize_url())
        
    def get_authorize_url(self):
        """
           return url for user to authenticate 
        """
        flow = self.get_flow()
        authorize_url = flow.step1_get_authorize_url()
        return authorize_url
        
    def get_credentials(self):
        """
            gets the credentials from the Storage
        """
        storage = Storage(
            Credentials, 
            'id', 
            self.request.user, 
            'credential'
        )
        credentials = storage.get()
        return credentials
        
    def get_flow(self):
        """
            return a OAuth2WebServerFlow instance
        """
        if self._flow == None:
            flow = OAuth2WebServerFlow(
                client_id=settings.GCAL_CLIENT_ID,
                client_secret=settings.GCAL_SECRET_ID,
                redirect_uri=settings.GCAL_REDIRECT_URL,
                scope= settings.GCAL_SCOPE,
                access_type = 'offline',
                approval_prompt = 'force',
            )
            self._flow = flow
        return self._flow
        
    def save_flow(self):
        """
            saves the state of the flow
        """
        flow = self.get_flow()
        user = self.request.user
        flow.params['state'] = xsrfutil.generate_token(
            settings.SECRET_KEY,
            user
        )
        flow = Flow(id=user, flow=flow)
        flow.save()
        
    def validate_credentials(self):
        """
            validates if the credentials are valid
        """
        credentials = self.get_credentials()
        return (credentials or not(credentials.invalid))
        

class AuthReturnView(LoginRequiredMixin, View):
    """
        AuthReturnView process the token recieved back from google.
        It verifies that the token has not been tampered and it
        stores the credentials in a Credentials Model.
        
        If authenticated the user gets redirected to 'GCAL_SUCCESS_URL' 
        otherwise it gets a HttpResponseBadRequest response.
    """
    _flow = None
    
    @staticmethod
    def delete_flow(flow):
        flow.delete()
    
    def get(self, request, *args, **kwargs):
        """
            validates, stores, and process the request
        """
        if self.validate_token():
            self.store()
            url = getattr(settings, 'GCAL_SUCCESS_URL', '/')
            return HttpResponseRedirect(url)
        return HttpResponseBadRequest()
        
    def get_flow(self):
        """
            gets a Flow instance from the database
        """
        if self._flow == None:
            flow = Flow.objects.get(id=self.request.user)
            self._flow = flow
        return self._flow
        
    def store(self):
        """
            stores credentials in the Credentials Model
        """
        flow = self.get_flow()
        credential = flow.step2_exchange(self.request.REQUEST)
        storage = Storage(
            Credentials, 
            'id', 
            self.request.user, 
            'credential'
        )
        storage.put(credential)
        self.delete_flow(flow)
        
    def validate_token(self):
        """
            validates that the token is authentic
        """
        return xsrfutil.validate_token(
                   settings.SECRET_KEY, 
                   self.request.REQUEST['state'],
                   self.request.user
               )
