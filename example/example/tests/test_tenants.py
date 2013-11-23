from django.test import TestCase
from django.db import connection as conn
from django.core.management import call_command
from example.models import Team


class TenantCreationTest(TestCase):
    def setUp(self):
        Team.objects.create(name='Something', domain='127.0.0.1', schema='something')

    def test_create_tenant(self):
        team = Team.objects.get(schema='something')
        self.assertEqual(team.name, 'Something')
        self.assertEqual(team.domain, '127.0.0.1')

