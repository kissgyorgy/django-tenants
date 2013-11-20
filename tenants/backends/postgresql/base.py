import re
from functools import wraps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.backends.postgresql_psycopg2 import base
from django.db import ProgrammingError
from django.db.models import get_model
from django.utils.functional import cached_property
from tenants.backends.postgresql.creation import SchemaAwareDatabaseCreation
from tenants.backends.postgresql.introspection import SchemaAwareDatabaseIntrospection
from tenants.utils import get_app_models


DatabaseError = base.DatabaseError
IntegrityError = base.IntegrityError


class DatabaseWrapper(base.DatabaseWrapper):
    # from the postgresql doc
    # http://www.postgresql.org/docs/9.1/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    VALID_IDENTIFIER_RE = re.compile('^[_a-zA-Z][_a-zA-Z0-9]{,62}$')

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        # Rather fail than expose some data which the tenant should not see!
        self._schema = None
        self.creation = SchemaAwareDatabaseCreation(self)
        self.introspection = SchemaAwareDatabaseIntrospection(self)

    def init_connection_state(self):
        super(DatabaseWrapper, self).init_connection_state()

        # For explanation: https://code.djangoproject.com/ticket/21453
        # This method is in transaction mode (PEP-249)
        self.set_autocommit(True)

        # Do it in every new connection, not in every cursor() request,
        # so there will be less queries
        self._set_search_path()

        # PEP-249, also respect database setting
        self.set_autocommit(False)

    def validate_schema(self, schema):
        """
        Validate schema name based on PostgreSQL documentation.

        See: http://www.postgresql.org/docs/9.1/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        It protect agains SQL injections, as only valid identifier will be allowed as schema names.
        Throws ValidationError if not valid, else return True
        """
        if not self.VALID_IDENTIFIER_RE.match(schema):
            raise ValidationError('Schema schema "%s" is not valid!' % schema)
        return True

    def requires_valid_schema(func):
        """
        Decorator for class methods which needs schema as the first argument to prevent SQL injection attacks.
        """
        @wraps(func)
        def wrapper(self, schema, *args, **kwargs):
            self.validate_schema(schema)
            return func(self, schema, *args, **kwargs)
        return wrapper

    @property
    def schema(self):
        """
        Currently active database schema.
        """
        return self._schema

    @schema.setter
    @requires_valid_schema
    def schema(self, schema):
        """
        Set schema and modify search_path accordingly.
        """
        self._schema = schema
        self._set_search_path()

    @requires_valid_schema
    def schema_exists(self, schema):
        """
        Check if this schema already exists in the db.

        Return True or False
        """
        cursor = self.cursor()
        # THis is the fastest method: http://stackoverflow.com/a/13877950/720077
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_namespace "
                       "WHERE nspname = %s)", [schema])
        return cursor.fetchone()[0]

    @requires_valid_schema
    def create_schema(self, schema):
        # we cannot use automatic escaping here, because schema name is not SQL string
        self.cursor().execute('CREATE SCHEMA "%s"' % schema)

    @requires_valid_schema
    def drop_schema(self, schema):
        """
        DROP schema with EVERY tables. No problem if schema doesn't exists.
        """
        self.cursor().execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % schema)

    def schema_is_public(self):
        """
        Tell if the current schema is the public schema or not.
        """
        return self.schema == self.PUBLIC_SCHEMA

    @cached_property
    def PUBLIC_SCHEMA(self):
        return getattr(settings, 'PUBLIC_SCHEMA', 'public')

    # We need to make it a property, otherwise it
    # "triggers some setup which tries to load the backend which in turn will fail cause it tries to retrigger that"
    # Basically, we can only construct this list in runtime, after the database backend properly built.
    @cached_property
    def TENANT_MODELS(self):
        """
        Return the list of tenant models generated from TENANT_APPS setting.
        """
        return [mod for appstr in settings.TENANT_APPS for mod in get_app_models(appstr)
                # South manipulate INSTALLED_APPS on sycdb, so this will just put those in
                # which South needs right now
                if appstr in settings.INSTALLED_APPS]

    @cached_property
    def SHARED_MODELS(self):
        """
        Return the list of shared models generated from the SHARED_APPS setting.
        """
        # SHARED_APPS is optional, so INSTALLED_APPS will be used if not available
        shared_apps = getattr(settings, 'SHARED_APPS', ())
        return [mod for appstr in shared_apps for mod in get_app_models(appstr)
                # check for South
                if appstr in settings.INSTALLED_APPS]

    @cached_property
    def FORCED_MODELS(self):
        """
        Return the list of models generated from SHARED_MODELS setting.

        SHARED_MODELS is an iterable which members are in a form of 'applabel.Model'
        e.g. 'auth.User' --> User model from django.contrib.auth app
        FIXME: public_models._meta.managed bypassed
        """
        installed_app_labels = [app.split('.')[-1] for app in settings.INSTALLED_APPS]

        models = []
        # SHARED_MODELS is optional, so it will be empty if the setting is not available
        for modstr in getattr(settings, 'FORCED_TO_PUBLIC_MODELS', ()):
            mod_split = modstr.split('.')
            # check for South
            if mod_split[-2] in installed_app_labels:
                models.append(get_model(mod_split[-2], mod_split[-1]))

        return models

    def _set_search_path(self):
        if not self._schema:
            # The connection will get reused, so make sure
            # we don't allow connecting until schema is set!
            self.connection = None
            raise ProgrammingError('Schema is not set on connection')

        # Database will search in schema from left to right when
        # looking for the object (table, index, sequence, etc.) so
        # if something exists on the tenant's schema, it will found that first
        if self._schema == self.PUBLIC_SCHEMA:
            self.cursor().execute('SET search_path TO %s', [self.PUBLIC_SCHEMA])
        else:
            self.cursor().execute('SET search_path TO %s, %s', [self._schema, self.PUBLIC_SCHEMA])
