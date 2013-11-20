from django.conf import settings
from django.db.models import get_app, get_models, get_model
from django.db import connection as conn


TENANT_MODEL = get_model(*settings.TENANT_MODEL.split("."))


def get_app_models(app_label):
    """Get all models from app_label or full app_string."""
    app = get_app(app_label.split('.')[-1])
    return get_models(app, include_auto_created=True)


def remove_www_and_port(hostname):
    """
    Removes www. from the beginning and :port from the end of the address.
    """
    hostname = hostname[4:] if hostname.startswith('www.') else hostname

    return hostname.split(':')[0]


def is_shared(model):
    """
    Tell if a given model is one of SHARED_APPS's models or in FORCED_TO_PUBLIC_MODELS settings.
    """
    return model in conn.SHARED_MODELS or model in conn.FORCED_MODELS

