from django.contrib import admin
from google_oauth.models import Credentials, Flow

class CredentialsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Credentials, CredentialsAdmin)
admin.site.register(Flow)
