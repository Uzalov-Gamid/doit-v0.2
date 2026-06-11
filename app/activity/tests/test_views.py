from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from activity.models import ActionLog


class ActionLogPageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='StrongPass12345',
            is_staff=True,
        )
        self.user = User.objects.create_user(username='student', password='StrongPass12345')
        ActionLog.objects.create(
            user=self.user,
            action_type=ActionLog.ACTION_TASK_CREATE,
            description='Создана тестовая задача.',
        )
        ActionLog.objects.create(
            user=self.user,
            action_type=ActionLog.ACTION_LOGIN,
            description='Пользователь вошел.',
        )

    def test_anonymous_user_is_redirected_from_log_page(self):
        response = self.client.get(reverse('activity:action_log_list'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('activity:action_log_list')}",
        )

    def test_regular_user_cannot_open_log_page(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('activity:action_log_list'))

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_open_log_page(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('activity:action_log_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Журнал действий')
        self.assertContains(response, 'Создана тестовая задача.')
        self.assertContains(response, 'Пользователь вошел.')

    def test_staff_user_can_filter_log_page_by_action_type(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse('activity:action_log_list'),
            {'action_type': ActionLog.ACTION_LOGIN},
        )

        self.assertContains(response, 'Пользователь вошел.')
        self.assertNotContains(response, 'Создана тестовая задача.')
        self.assertEqual(response.context['selected_action_type'], ActionLog.ACTION_LOGIN)

    def test_staff_dashboard_has_log_page_link(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertContains(response, 'Журнал действий')
        self.assertContains(response, reverse('activity:action_log_list'))
