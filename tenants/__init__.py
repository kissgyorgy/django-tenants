from django.conf import settings
from django.db import connection as conn
from django.core.exceptions import ImproperlyConfigured

recommended_config = """
You should put 'tenants' at the end of INSTALLED_APPS like this:
INSTALLED_APPS = TENANT_APPS + SHARED_APPS + ('tenants',)
This is neccesary to overwrite built-in django management commands with their schema-aware implementations.
"""
# Make a bunch of tests for configuration recommendations
# These are best practices basically, to avoid hard to find bugs, unexpected behaviour
if not hasattr(settings, 'TENANT_APPS'):
    raise ImproperlyConfigured('TENANT_APPS setting not set')

if not settings.TENANT_APPS:
    raise ImproperlyConfigured("TENANT_APPS is empty. Maybe you don't need this app?")

if 'tenants' in settings.SHARED_APPS + settings.TENANT_APPS:
    raise ImproperlyConfigured(recommended_config)

if not (settings.TENANT_APPS + settings.SHARED_APPS + ('tenants', ) == settings.INSTALLED_APPS):
    raise ImproperlyConfigured(recommended_config)

#for pm in conn.FORCED_MODELS:
#    if pm not in conn.SHARED_MODELS:
#        raise ImproperlyConfigured('Every PUBLIC_MODEL should belong to one of the SHARED_APPS '
#                                   'to avoid unexpected behaviour.')

# check if TENANT_MODEL's app is in installed apps

TENANT_APP_LABELS = [app.split('.')[-1] for app in settings.TENANT_APPS]

# SHARED_APPS and FORCED_TO_PUBLIC_MODELS settings are optional, so make it an empty tuple if not exists
SHARED_APP_LABELS = [app.split('.')[-1] for app in getattr(settings, 'SHARED_APPS', ())]
FORCED_MODELS = getattr(settings, 'FORCED_TO_PUBLIC_MODELS', ())
