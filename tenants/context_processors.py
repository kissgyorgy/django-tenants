"""
Include this in REQUEST_CONTEXT_PROCESSORS setting if you want {{ tenant }} in templates.
Then, you can use {{ tenant.domain }}, {{ tenant.schema }}, {{ tenant.name }} etc
"""


def tenant(request):
    return {'tenant': request.tenant}
