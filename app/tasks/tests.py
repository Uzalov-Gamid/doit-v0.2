from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class DashboardAccessTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get('/')

        self.assertRedirects(response, f"{reverse('accounts:login')}?next=/")

    def test_logged_user_can_open_dashboard(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        self.client.force_login(user)

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Личный кабинет')
