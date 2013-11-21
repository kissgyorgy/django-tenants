from django.db.backends.postgresql_psycopg2.introspection import DatabaseIntrospection


class SchemaAwareDatabaseIntrospection(DatabaseIntrospection):
    def get_table_list(self, cursor):
        """Returns a list of table names in the current schema."""
        # FIXME: query based on schema and models
        cursor.execute("""
            SELECT c.relname
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r', 'v', '')
                AND n.nspname = %s
                AND pg_catalog.pg_table_is_visible(c.oid)""", [self.connection.schema])
        return [row[0] for row in cursor.fetchall() if row[0] not in self.ignored_tables]
