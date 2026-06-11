from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tasks.models import Task

from .models import ActionLog


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

    def test_status_change_is_logged(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        task = Task.objects.create(user=user, title='Сменить статус')
        self.client.force_login(user)

        self.client.post(reverse('tasks:task_status', args=(task.pk,)), {'status': Task.STATUS_DONE})

        self.assertTrue(ActionLog.objects.filter(action_type=ActionLog.ACTION_STATUS_CHANGE).exists())
