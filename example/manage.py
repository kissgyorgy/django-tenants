#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

    from django.core.management import execute_from_command_line

    # we can test multiple "domains" from development machine
    # by connecting from 127.0.0.1 and another internal IP, maybe even from WAN
    if len(sys.argv) == 2 and sys.argv[1] == 'runserver':
        sys.argv.append('0.0.0.0:8000')

    execute_from_command_line(sys.argv)
