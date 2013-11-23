example project need to be in your ``PATH``
See: http://pytest-django.readthedocs.org/en/latest/faq.html#i-see-an-error-saying-could-not-import-myproject-settings

To run the tests:

.. code-block:: bash

    # from the directory where manage.py is:
    $ PYTHONPATH=example DJANGO_SETTINGS_MODULE=settings py.test
