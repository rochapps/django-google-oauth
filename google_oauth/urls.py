from django.conf.urls.defaults import patterns, include, url
from google_oauth.views import AuthCredentials, AuthReturnView


urlpatterns = patterns('',
    url(r'^$', AuthCredentials.as_view(), 
        name="google_auth"),
    url(r'^oauth2callback', AuthReturnView.as_view(), 
        name="google_auth_return"),
)
