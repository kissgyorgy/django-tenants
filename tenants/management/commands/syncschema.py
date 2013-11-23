from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection as conn
from django.db.models.signals import post_syncdb
from django.contrib.auth.management import create_permissions, create_superuser
from django.contrib.auth import models as auth_app
from tenants import TENANT_APP_LABELS, FORCED_MODELS
from tenants.utils import is_shared


class Command(BaseCommand):
    args = '<schema1 schema2 ...>'
    help = 'Sync schemas to the database.'

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        # First check if public schema is synced already
        write = self.stdout.write
        if len(args) == 0:
            raise CommandError('You need to specify schema names to sync!')

        if args[0] != conn.PUBLIC_SCHEMA:
            conn.schema = conn.PUBLIC_SCHEMA
            # There are no tables in public schema
            if not conn.introspection.table_names():
                raise CommandError('You should sync the public schema first!')

        for schema in args:
            conn.schema = schema
            if not conn.schema_exists(schema):
                conn.create_schema(schema)
            auth_user_not_in_tenant = 'auth.User' in FORCED_MODELS or 'auth' not in TENANT_APP_LABELS
            if (conn.schema_is_public() and not is_shared(auth_app.User) or
               (not conn.schema_is_public() and auth_user_not_in_tenant)):
                    if verbosity > 1:
                        write("Disconnect auth.User signal handlers, as it is not synced...")
                    post_syncdb.disconnect(create_permissions,
                                           dispatch_uid="django.contrib.auth.management.create_permissions")
                    post_syncdb.disconnect(create_superuser, sender=auth_app,
                                           dispatch_uid="django.contrib.auth.management.create_superuser")

            call_command('syncdb', **options)
