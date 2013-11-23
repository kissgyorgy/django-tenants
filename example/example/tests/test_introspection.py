from django.core.management import call_command
from django.db import connection as conn
from django.db.backends.postgresql_psycopg2.base import DatabaseIntrospection
from pytest import mark, fixture


# mark every test needs database connection
pytestmark = mark.django_db

@fixture
def orig_intro():
    return DatabaseIntrospection(conn)


def test_orig_and_custom_backend_on_public_schema_after_syncdb(settings, orig_intro):
    assert conn.schema == conn.PUBLIC_SCHEMA

    settings.TENANT_APPS = ('django.contrib.admin', 'django.contrib.auth',)
    settings.SHARED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'example',
    )
    settings.INSTALLED_APPS = settings.TENANT_APPS + settings.SHARED_APPS + ('tenants',)
    settings.FORCED_TO_PUBLIC_MODELS = ('auth.User',)

    call_command('syncdb')

    table_list_should_be = [u'auth_group', u'auth_group_permissions',
                            u'django_admin_log', u'auth_permission',
                            u'django_session', u'auth_user_groups',
                            u'auth_user_user_permissions', u'example_team',
                            u'auth_user', u'django_content_type']

    # with the original postgresql_psycopg2 backend
    assert table_list_should_be == orig_intro.get_table_list(conn.cursor())

    # with django-tenants custom backend
    assert table_list_should_be == conn.introspection.get_table_list(conn.cursor())
