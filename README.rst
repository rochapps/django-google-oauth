==========
Google oauth 2.0
==========

google_oauth helps you authenticate your application, and ask for user permissions.
Once a user has granted access to your application, his credentials are stored 
in the database for later retrival. 

You can check for credentials like this:

    storage = Storage(CredentialsModel, 'id', 
        instance.attorney.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        #if user is not authenticated do whatever you want here
        #raise Exception("You need to authenticate your account")
    else:
        #build a service
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('calendar', 'v3', http=http)
        
Requirements
============
    1. google-api-python-client
    2. mock (for testing only)

Usage
=====
    1. Install application
    2. syncdb
    3. add url(r'^auth/google/', include('google_oauth.urls')), to your urls.
    4. set the following settings in your settings.py file 
        1. GCAL_SCOPE = 'https://www.googleapis.com/auth/calendar'
        2. GCAL_REDIRECT_URL
        3. GCAL_CLIENT_ID
        4. GCAL_SECRET_ID
        5. GCAL_SUCCESS_URL
        6. GCAL_ACCESS_TYPE


www.rochapps.com
================
We built legal management software solutions for attorneys that want to move their practice to the cloud
