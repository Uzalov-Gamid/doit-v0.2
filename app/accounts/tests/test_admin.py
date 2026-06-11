from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AdminAccessTests(TestCase):
    def test_anonymous_user_is_redirected_from_admin(self):
        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_regular_user_is_redirected_from_admin(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        self.client.force_login(user)

        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_superuser_can_open_admin(self):
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='StrongPass12345',
        )
        self.client.force_login(admin)

        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 200)
