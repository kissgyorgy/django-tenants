from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection as conn
from django.db.models.signals import post_syncdb
from django.contrib.auth.management import create_permissions, create_superuser
from django.contrib.auth import models as auth_app


class Command(BaseCommand):
    args = '<tenant name>'
    help = 'Create a tenant'

    def handle(self, *args, **options):
        pass

    def get_version(self):
        return 'Required Django version: 1.6'

