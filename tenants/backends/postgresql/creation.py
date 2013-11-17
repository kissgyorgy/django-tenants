from django.db.backends.postgresql_psycopg2.creation import DatabaseCreation


class ShemaAwareDatabaseCreation(DatabaseCreation):
    def _table_prefix(self, model):
        """
        Return the proper table prefix based on SHARED_APPS, TENANT_APPS, PUBLIC_MODELS settings and current schema.
        """
        conn = self.connection
        qn = conn.ops.quote_name

        if model in conn.PUBLIC_MODELS:
            return qn(conn.PUBLIC_SCHEMA) + '.'

        elif model in conn.TENANT_MODELS:
            return qn(conn.schema) + '.'

        elif model in conn.SHARED_MODELS:
            return qn(conn.PUBLIC_SCHEMA)

        else:
            # models only in SHARED_APPS models don't need table prefix, because
            # when we need to operate on public schema, search path is set exclusively to it.
            return ''
