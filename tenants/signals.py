from django.dispatch import Signal

post_schema_create = Signal(providing_args=['tenant'])
post_schema_create.__doc__ = """
Sent after a tenant's schema has been created.

It's ideal for starting the database syncing process after this with a task queue!
"""

pre_schema_delete = Signal(providing_args=['tenant'])
pre_schema_delete.__doc__ = """Sent immediately before a tenant's schema being deleted."""
