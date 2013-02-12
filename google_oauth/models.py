from django.contrib.auth.models import User
from django.db import models

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField


class Flow(models.Model):
    """
        class to save flow objects in a multitreaded environment
    """
    id = models.ForeignKey(User, primary_key=True)
    flow = FlowField()


class Credentials(models.Model):
    """
        saves user oauth credentials for later use
    """
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()
