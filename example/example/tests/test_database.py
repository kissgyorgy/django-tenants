from django.db import connection as conn
from django.core.management import call_command
from pytest import mark


@mark.django_db
def test_create_new_schema2():
    schema = 'newschema'
    call_command('syncschema', schema)
    cur = conn.cursor()
    cur.execute('SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_namespace WHERE nspname = %s)', [schema])

    assert cur.fetchone()[0] is True
