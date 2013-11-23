from django.db import connection as threadlocal_conn
from pytest import mark, fixture

# mark everything as a database test in this module
# http://pytest-django.readthedocs.org/en/latest/database.html
pytestmark = mark.django_db


@fixture
def conn(settings):
    """
    Makes a "virgin" connection object.

    If we simply import django.db.connection, test would produce unexpected results,
    because it's a thread local, so one test would change it before another executes.
    """
    from tenants.backends.postgresql.base import DatabaseWrapper
    return DatabaseWrapper(settings.DATABASES['default'])


def test_search_path():
    c = threadlocal_conn.cursor()
    c.execute('SHOW search_path')
    search_path = c.fetchone()[0]
    assert search_path == 'public'


def test_schema_can_be_set():
    assert threadlocal_conn.schema == 'public'
    threadlocal_conn.schema = 'something'
    assert threadlocal_conn.schema == 'something'


def test_initial_schame_should_be_public():
    assert threadlocal_conn.schema == 'public'


def test_changing_schema_change_search_path():
    assert threadlocal_conn.schema == 'public'
    threadlocal_conn.schema = 'newtenant'
    c = threadlocal_conn.cursor()
    c.execute('SHOW search_path')
    assert c.fetchone()[0] == 'newtenant, public'


def test_schema_exists_function():
    cur = threadlocal_conn.cursor()
    cur.execute('CREATE SCHEMA tenantname')
    assert threadlocal_conn.schema_exists('tenantname') is True
    cur.execute('SELECT current_database()')
