from django.contrib.auth.models import User
from django.test import TestCase

from accounts.forms import RegistrationForm


class RegistrationFormTests(TestCase):
    def test_email_is_optional(self):
        form = RegistrationForm(
            data={
                'username': 'student',
                'password1': 'StrongPass12345',
                'password2': 'StrongPass12345',
            }
        )

        self.assertTrue(form.is_valid())

    def test_duplicate_username_is_invalid(self):
        User.objects.create_user(username='student', password='StrongPass12345')

        form = RegistrationForm(
            data={
                'username': 'student',
                'email': 'student@example.com',
                'password1': 'StrongPass12345',
                'password2': 'StrongPass12345',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_password_mismatch_is_invalid(self):
        form = RegistrationForm(
            data={
                'username': 'student',
                'password1': 'StrongPass12345',
                'password2': 'OtherPass12345',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
