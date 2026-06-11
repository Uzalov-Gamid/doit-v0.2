from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import RegistrationForm


class AccountsAuthTests(TestCase):
    def test_login_page_is_available(self):
        response = self.client.get(reverse('accounts:login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход')

    def test_register_page_is_available(self):
        response = self.client.get(reverse('accounts:register'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')

    def test_user_can_register(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'student',
                'email': 'student@example.com',
                'password1': 'StrongPass12345',
                'password2': 'StrongPass12345',
            },
        )

        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertTrue(User.objects.filter(username='student').exists())

    def test_login_redirects_authenticated_user_to_dashboard(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        self.client.force_login(user)

        response = self.client.get(reverse('accounts:login'))

        self.assertRedirects(response, reverse('tasks:dashboard'))


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


class AccountsFrontendTests(TestCase):
    def test_login_page_renders_expected_form_and_links(self):
        response = self.client.get(reverse('accounts:login'))

        self.assertContains(response, '<form method="post" class="form">')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, reverse('accounts:register'))
        self.assertContains(response, 'css/styles.css')
        self.assertContains(response, 'js/app.js')

    def test_register_page_renders_expected_form_fields(self):
        response = self.client.get(reverse('accounts:register'))

        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')
        self.assertContains(response, reverse('accounts:login'))
