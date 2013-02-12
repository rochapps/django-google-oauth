from django.contrib.auth.models import User
from django.db import models

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField

# The Flow could also be stored in memcache since it is short lived.


class Flow(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    flow = FlowField()


class Credentials(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()
