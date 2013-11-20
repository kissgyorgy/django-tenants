from django.db import models, connection as conn
from django.core.exceptions import PermissionDenied
from tenants.backends.postgresql.base import IntegrityError
from tenants.signals import post_schema_create, pre_schema_delete


class BaseTenant(models.Model):
    domain = models.CharField(max_length=128, unique=True,
                              help_text='Domain name without www and port')

    schema = models.CharField(max_length=63, unique=True,
                              help_text='Database schema name')

    class Meta:
        abstract = True

    def save(self, create_schema=True, *args, **kwargs):
        """
        Save the tenant instance in the database after creating the related database schema.
        """
        new = self.pk is None
        if not new and conn.schema not in (self.schema, conn.PUBLIC_SCHEMA):
            raise PermissionDenied("Can't update tenant outside it's own schema or the public schema. "
                                   "Current schema is %s." % conn.schema)

        if new and create_schema:
            conn.validate_schema(self.schema)
            if conn.schema_exists(self.schema):
                raise IntegrityError('Schema %s already exists' % self.schema)

            # CREATE schema in the database, but not actually sync the tables for it
            # kind of "reservation" for the name. Put the syncdb process in a worker thread!
            conn.create_schema(self.schema)
            post_schema_create.send(sender=BaseTenant, tenant=self)

        # only save tenant instance in the database if everything was ok
        super(BaseTenant, self).save(*args, **kwargs)

    def delete(self, drop_schema=False, *args, **kwargs):
        """
        Delete the tenant instance from the database after dropping the related database schema.
        """
        if conn.schema not in (self.schema, conn.PUBLIC_SCHEMA):
            raise PermissionDenied("Can't delete tenant outside it's own schema or the public schema. "
                                   "Current schema is %s." % conn.schema)

        if drop_schema and conn.schema_exists(self.schema):
            pre_schema_delete.send(sender=BaseTenant, tenant=self)
            conn.drop_schema(self.schema)

        super(BaseTenant, self).delete(*args, **kwargs)
