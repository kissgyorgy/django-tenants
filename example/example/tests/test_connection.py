from django.db.models import get_models
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


# FIXME ezt kijavitani, valtozo konfiggal tesztelni
def test_TENANT_MODELS():
    import django.contrib.auth.models as auth_app
    auth_models = get_models(auth_app)
    assert set(auth_models).issubset(set(threadlocal_conn.TENANT_MODELS))


def test_schema_exists_function():
    cur = threadlocal_conn.cursor()
    cur.execute('CREATE SCHEMA tenantname')
    assert threadlocal_conn.schema_exists('tenantname') is True
    cur.execute('SELECT current_database()')


# settings fixture comes from pytest-django.
# it will be restored to the original state when the test function ends
def test_empty_settings_connection_properties(settings, conn):
    settings.TENANT_APPS = ()
    settings.SHARED_APPS = ()
    settings.TENANT_MODEL = None
    settings.SHARED_MODELS = ()
    settings.INSTALLED_APPS = settings.TENANT_APPS

    from example.models import Team

    assert conn.TENANT_MODELS == []
    assert conn.SHARED_MODELS == []
    assert conn.FORCED_MODELS == []

