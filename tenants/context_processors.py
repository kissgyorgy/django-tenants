"""
Include this in REQUEST_CONTEXT_PROCESSORS setting if you want {{ tenant }} in templates.
"""


def tenant(request):
    return {'tenant': request.tenant}
