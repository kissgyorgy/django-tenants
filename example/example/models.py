from django.db import models
from tenants.models import BaseTenant


class Team(BaseTenant):
    name = models.CharField(max_length=255)
