from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
