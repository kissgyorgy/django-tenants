import re
from django.conf import settings
from django.db.backends.postgresql_psycopg2 import base
from django.db import ProgrammingError


# from the postgresql doc
# http://www.postgresql.org/docs/9.1/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
SQL_IDENTIFIER_PATTERN = re.compile('^[_a-zA-Z][_a-zA-Z0-9]{,62}$')

PUBLIC_SCHEMA = getattr(settings, 'PUBLIC_SCHEMA', 'public')

DatabaseError = base.DatabaseError
IntegrityError = base.IntegrityError


class DatabaseWrapper(base.DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self._schema = None

    def init_connection_state(self):
        super(DatabaseWrapper, self).init_connection_state()

        # For explanation: https://code.djangoproject.com/ticket/21453
        # This method is in transaction mode (PEP-249)
        self.set_autocommit(True)

        # Do it in every new connection, not in every cursor() request,
        # so it might result less queries
        self._set_search_path()

        # PEP-249, also respect database setting
        self.set_autocommit(False)

    def set_schema(self, schema):
        """Set schema and modify search_path accordingly."""
        self._schema = schema
        self._set_search_path()

    def get_schema(self):
        """Get currently active database schema."""
        return self._schema

    @staticmethod
    def schema_valid(identifier):
        return SQL_IDENTIFIER_PATTERN.match(identifier)

    def schema_exists(self, schema):
        """
        Check if this schema already exists in the db.

        Return True or False
        """
        cursor = self.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata "
                       "WHERE schema_name = %s)", [schema])
        return cursor.fetchone()[0]

    def create_schema(self, schema):
        self.cursor().execute('CREATE SCHEMA %s', [schema])

    def drop_schema(self, schema):
        """DROP schema with EVERY tables."""
        self.cursor().execute('DROP SCHEMA %s CASCADE', [schema])

    def _set_search_path(self):
        if not self._schema:
            # The connection will get reused, so make sure
            # we don't allow connecting until schema is set!
            self.connection = None
            raise ProgrammingError('Schema is not set on connection')

        # Database will search in schema from left to right when
        # looking for the object (table, index, sequence, etc.)
        # so if something exists on the tenant schema, it will found that first
        if self._schema == PUBLIC_SCHEMA:
            self.cursor().execute('SET search_path TO %s', [PUBLIC_SCHEMA])
        else:
            self.cursor().execute('SET search_path TO %s,%s', [self._schema, PUBLIC_SCHEMA])
