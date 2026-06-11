from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tasks.models import Task

from .models import ActionLog
from .services import log_action


class ActivityLogTests(TestCase):
    def test_login_and_logout_are_logged(self):
        User.objects.create_user(username='student', password='StrongPass12345')

        self.client.login(username='student', password='StrongPass12345')
        self.client.post(reverse('accounts:logout'))

        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_LOGIN).exists())
        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_LOGOUT).exists())

    def test_registration_is_logged(self):
        self.client.post(
            reverse('accounts:register'),
            {
                'username': 'student',
                'email': 'student@example.com',
                'password1': 'StrongPass12345',
                'password2': 'StrongPass12345',
            },
        )

        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_REGISTER).exists())

    def test_task_create_is_logged(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        self.client.force_login(user)

        self.client.post(
            reverse('tasks:task_create'),
            {
                'title': 'Проверить журнал',
                'description': '',
                'status': Task.STATUS_NEW,
                'due_date': '',
            },
        )

        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_TASK_CREATE).exists())

    def test_task_update_is_logged(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        task = Task.objects.create(user=user, title='Старая задача')
        self.client.force_login(user)

        self.client.post(
            reverse('tasks:task_update', args=(task.pk,)),
            {
                'title': 'Новая задача',
                'description': '',
                'status': Task.STATUS_NEW,
                'due_date': '',
            },
        )

        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_TASK_UPDATE).exists())

    def test_task_delete_is_logged(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        task = Task.objects.create(user=user, title='Удалить задачу')
        self.client.force_login(user)

        self.client.post(reverse('tasks:task_delete', args=(task.pk,)))

        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_TASK_DELETE).exists())

    def test_status_change_is_logged(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        task = Task.objects.create(user=user, title='Сменить статус')
        self.client.force_login(user)

        self.client.post(reverse('tasks:task_status', args=(task.pk,)), {'status': Task.STATUS_DONE})

        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_STATUS_CHANGE).exists())

    def test_log_action_allows_missing_user(self):
        log_action(None, ActionLog.ACTION_LOGOUT, 'Анонимный выход.')

        log = ActionLog.objects.get()
        self.assertIsNone(log.user)
        self.assertEqual(log.action_type, ActionLog.ACTION_LOGOUT)

    def test_action_log_string_contains_user_and_action(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        log = ActionLog.objects.create(
            user=user,
            action_type=ActionLog.ACTION_TASK_CREATE,
            description='Создана задача.',
        )

        self.assertIn('student', str(log))
        self.assertIn('Создание задачи', str(log))


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
