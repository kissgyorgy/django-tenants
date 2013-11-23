from django.conf import settings


TENANT_APP_LABELS = [app.split('.')[-1] for app in settings.TENANT_APPS]

# SHARED_APPS and FORCED_TO_PUBLIC_MODELS settings are optional, so make it an empty tuple if not exists
SHARED_APP_LABELS = [app.split('.')[-1] for app in getattr(settings, 'SHARED_APPS', ())]
FORCED_MODELS = getattr(settings, 'FORCED_TO_PUBLIC_MODELS', ())


def remove_www_and_port(hostname):
    """
    Removes www. from the beginning and :port from the end of the address.
    """
    hostname = hostname[4:] if hostname.startswith('www.') else hostname

    return hostname.split(':')[0]


def is_shared(model):
    """
    Tell if a given model is one of SHARED_APPS's models
    or in FORCED_TO_PUBLIC_MODELS settings.
    """
    return model._meta.app_label in SHARED_APP_LABELS or \
           dotted_name(model) in FORCED_MODELS


def dotted_name(model):
    """
    return the "applabel.ModelClass" for a given model.
    """
    return model._meta.app_label + '.' + model._meta.object_name
