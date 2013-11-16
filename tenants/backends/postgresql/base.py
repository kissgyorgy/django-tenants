from django.conf import settings
from django.db.backends.postgresql_psycopg2 import base


PUBLIC_SCHEMA = getattr(settings, 'PUBLIC_SCHEMA', 'public')
DatabaseError = base.DatabaseError
IntegrityError = base.IntegrityError


class DatabaseWrapper(base.DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self._schema = PUBLIC_SCHEMA

    def init_connection_state(self):
        super(DatabaseWrapper, self).init_connection_state()

        # For explanation: https://code.djangoproject.com/ticket/21453
        self.set_autocommit(True)

        # Do it in every new connection, not in every cursor() request,
        # so it might result less queries
        self._set_search_path()

        # PEP-249, also respect database setting
        self.set_autocommit(False)

    def _set_search_path(self):
        if not self._schema:
            raise RuntimeError('Schema is not set on connection')
        # Database will search in schema from left to right when
        # looking for the object (table, index, sequence, etc.)
        # so if something exists on the tenant schema, it will found that first
        if self._schema == PUBLIC_SCHEMA:
            self.connection.cursor().execute('SET search_path TO %s', [PUBLIC_SCHEMA])
        else:
            self.connection.cursor().execute('SET search_path TO %s,%s', [self._schema, PUBLIC_SCHEMA])

    def set_schema(self, schema):
        self._schema = schema

    def get_schema(self):
        return self._schema
