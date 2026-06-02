from django.test import TestCase
from django.core import mail


class EmailBackendTests(TestCase):
    def test_email_connection_exists(self):
        connection = mail.get_connection()
        self.assertIsNotNone(connection)