import unittest
import urllib

from mock import patch
from oauth2client import xsrfutil
from oauth2client.django_orm import Storage
from oauth2client.client import OAuth2WebServerFlow

from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.test.client import RequestFactory

from google_oauth.views import LoginRequiredMixin
from google_oauth.views import AuthCredentials
from google_oauth.views import AuthReturnView
from google_oauth.models import Credentials, Flow


class AuthCredentialsTests(TestCase):

    def setUp(self):
        self.password = 'password'
        self.user = User.objects.create_superuser('victor',
            'info@rochapps.com', self.password)
        self.factory = RequestFactory()
        self.url = reverse('google_auth')
        self.request = self.make_request()
        self.login()
        self.view = self.initiate_view()
        
    def login(self):
        self.client.login(
            username=self.user.email, 
            password=self.password
        )
        
    def make_request(self):
        request = self.factory.get(self.url)
        request.user = self.user
        return request
        
    def initiate_view(self):
        view = AuthCredentials(request=self.request)
        return view
        
    def test_get(self):
        with patch.object(AuthCredentials, 'validate_credentials') as validate:
            validate.return_value = True
            response = self.view.get(self.request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.get('location'), 
                getattr(settings, 'GCAL_SUCCESS_URL', '/')
            )
            validate.return_value = False
            response = self.view.get(self.request)
            self.assertEqual(
                response.get('location'),
                self.view.get_authorize_url(),
            )
        
    def test_get_authorize_url(self):
        google_url = 'https://accounts.google.com/o/oauth2/auth?'
        params = {
            'client_id': settings.GCAL_CLIENT_ID,
            'redirect_uri': settings.GCAL_REDIRECT_URL,
            'scope': settings.GCAL_SCOPE,
            'access_type': 'offline',
            'approval_prompt': 'force',
        }
        auth_url = self.view.get_authorize_url()
        self.assertIn(google_url, auth_url)
        for key, value in params.items():
            self.assertIn(urllib.urlencode({key:value}), auth_url)
            
    def test_get_credentials(self):
        credentials = self.view.get_credentials() #User does have credentials
        self.assertFalse(credentials)
        #tests that the credentials are being retrived
        with patch.object(Storage, 'get') as storage:
            credentials = self.view.get_credentials()
            storage.assert_called_once_with()
            
    def test_get_flow(self):
        """tests that get flow returns a OAuth2WebServerFlow object"""
        
        flow = self.view.get_flow()
        self.assertIsInstance(flow, OAuth2WebServerFlow)
        
    def test_save_flow(self):
        with patch.object(Flow, 'save') as save_flow:
            self.view.save_flow()
            save_flow.assert_called_once_with()
        self.view.save_flow()
        self.assertEqual(Flow.objects.count(), 1)   
        
            
    def test_validate_credentials(self):
        self.assertFalse(self.view.get_credentials())
        with patch.object(AuthCredentials, 'get_credentials') as credentials:
            credentials.return_value = True
            self.assertTrue(self.view.get_credentials())
            
            
class AuthReturnViewTests(TestCase):

    def setUp(self):
        self.password = 'password'
        self.user = User.objects.create_superuser('victor',
            'info@rochapps.com', self.password)
        self.factory = RequestFactory()
        self.url = reverse('google_auth_return')
        self.request = self.make_request()
        self.login()
        self.view = self.initiate_view()
        
    def login(self):
        self.client.login(
            username=self.user.email, 
            password=self.password
        )
        
    def make_request(self):
        request = self.factory.get(
            self.url, 
        )
        request.user = self.user
        return request
        
    def initiate_view(self):
        view = AuthReturnView(request=self.request)
        return view
        
    def test_delete_flow(self):
        flow = Flow()
        with patch.object(flow, 'delete') as delete:
            self.view.delete_flow(flow)
            delete.assert_called_once_with()
    
    def test_get(self):
        with patch.object(AuthReturnView, 'validate_token') as validate:
            validate.return_value = True
            with patch.object(AuthReturnView, 'store') as store:
                response = self.view.get(self.request)
                store.assert_called_once_with()
                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.get('location'),
                    getattr(settings, 'GCAL_SUCCESS_URL', '/')
                )
            validate.return_value = False
            response = self.view.get(self.request)
            self.assertEqual(response.status_code, 400)
        
    def test_get_flow(self):
        self.assertRaises(ObjectDoesNotExist, self.view.get_flow)
        with patch.object(Flow, 'objects') as objects:
            with patch.object(objects, 'get') as get:
                get.return_value = True
                flow = self.view.get_flow()
                self.assertTrue(flow)
        self.view._flow = True
        flow = self.view.get_flow()
        self.assertTrue(flow)
    
    #TODO: needs test    
    def test_store(self):
        pass
        
    def test_validate_token(self):

        request = self.factory.get(
            self.url, 
            {'state': 'aw1231jass'} #forged token
        )
        request.user = self.user
        view = AuthReturnView(request=request)
        valid = view.validate_token()
        self.assertFalse(valid)
        
        #generate valid token for user
        token = xsrfutil.generate_token(
            settings.SECRET_KEY,
            self.user
        )
        request = self.factory.get(
            self.url, 
            {'state': token} #valid token
        )
        request.user = self.user
        view = AuthReturnView(request=request)
        valid = view.validate_token()
        self.assertTrue(valid)
