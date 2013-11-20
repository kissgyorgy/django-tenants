from django.db import connection
from django.shortcuts import get_object_or_404
from tenants.utils import remove_www_and_port


class TenantMiddleware(object):
    """
    This middleware should be placed at the very top of the middleware stack.
    Selects the proper database schema using the request host. Can fail in
    various ways which is better than corrupting or revealing data...
    """
    def process_request(self, request):

        hostname_without_port = remove_www_and_port(request.get_host())
        request.tenant = get_object_or_404(connection.TENANT_MODEL, domain=hostname_without_port)

        # this automatically set the correct search path
        connection.schema = request.tenant.schema
