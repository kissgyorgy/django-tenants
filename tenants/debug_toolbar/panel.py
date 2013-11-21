"""
Schema panel for django-debug-toolbar.
"""

from collections import OrderedDict
from debug_toolbar.panels import DebugPanel
from django.db import connection as conn


class TenantsDebugPanel(DebugPanel):
    name = 'Tenants'
    template = 'tenants/debug_panel.html'
    has_content = True

    def nav_title(self):
        return 'Tenants'

    def nav_subtitle(self):
        return '"%s" schema' % conn.schema

    def url(self):
        return ''

    def title(self):
        return 'Tenants'

    def process_response(self, request, response):
        tenant = conn.TENANT_MODEL.objects.get(schema=conn.schema)
        c = conn.cursor()
        c.execute('SHOW search_path')
        search_path = c.fetchone()[0]
        self.record_stats({
            'tenant': {'domain': tenant.domain, 'schema': tenant.schema},
            'connection': [('schema', conn.schema), ('PUBLIC_SCHEMA', conn.PUBLIC_SCHEMA),
                           ('schema_is_public()', conn.schema_is_public()),
                           ('search_path', search_path),
                           ('TENANT_MODELS', conn.TENANT_MODELS),
                           ('SHARED_MODELS', conn.SHARED_MODELS),
                           ('FORCED_MODELS:', conn.FORCED_MODELS)]
        })
