from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Task


class DashboardAccessTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get('/')

        self.assertRedirects(response, f"{reverse('accounts:login')}?next=/")

    def test_logged_user_can_open_dashboard(self):
        user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass12345',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Личный кабинет')
        self.assertContains(response, 'student@example.com')
        self.assertContains(response, 'user')

    def test_staff_user_sees_admin_role_and_link(self):
        admin = User.objects.create_user(
            username='admin',
            password='StrongPass12345',
            is_staff=True,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertContains(response, 'admin')
        self.assertContains(response, '/admin/')

    def test_user_sees_only_own_tasks(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        other = User.objects.create_user(username='other', password='StrongPass12345')
        Task.objects.create(user=user, title='Моя задача')
        Task.objects.create(user=other, title='Чужая задача')
        self.client.force_login(user)

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertContains(response, 'Моя задача')
        self.assertNotContains(response, 'Чужая задача')


class TaskCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='StrongPass12345')
        self.client.force_login(self.user)

    def test_user_can_create_task(self):
        response = self.client.post(
            reverse('tasks:task_create'),
            {
                'title': 'Подготовить README',
                'description': 'Описать запуск проекта',
                'status': Task.STATUS_NEW,
                'due_date': '2026-06-20',
            },
        )

        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertTrue(Task.objects.filter(user=self.user, title='Подготовить README').exists())

    def test_user_can_update_task(self):
        task = Task.objects.create(user=self.user, title='Старая задача')

        response = self.client.post(
            reverse('tasks:task_update', args=(task.pk,)),
            {
                'title': 'Обновленная задача',
                'description': '',
                'status': Task.STATUS_IN_PROGRESS,
                'due_date': '',
            },
        )

        task.refresh_from_db()
        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertEqual(task.title, 'Обновленная задача')
        self.assertEqual(task.status, Task.STATUS_IN_PROGRESS)

    def test_user_can_delete_task(self):
        task = Task.objects.create(user=self.user, title='Удалить задачу')

        response = self.client.post(reverse('tasks:task_delete', args=(task.pk,)))

        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_user_can_change_status(self):
        task = Task.objects.create(user=self.user, title='Сменить статус')

        response = self.client.post(
            reverse('tasks:task_status', args=(task.pk,)),
            {'status': Task.STATUS_DONE},
        )

        task.refresh_from_db()
        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertEqual(task.status, Task.STATUS_DONE)

    def test_user_cannot_update_another_user_task(self):
        other = User.objects.create_user(username='other', password='StrongPass12345')
        task = Task.objects.create(user=other, title='Чужая задача')

        response = self.client.get(reverse('tasks:task_update', args=(task.pk,)))

        self.assertEqual(response.status_code, 404)


class TaskSearchAndStatsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='StrongPass12345')
        self.client.force_login(self.user)
        Task.objects.create(user=self.user, title='Купить продукты', status=Task.STATUS_NEW)
        Task.objects.create(
            user=self.user,
            title='Учебный отчет',
            description='Подготовить документацию',
            status=Task.STATUS_IN_PROGRESS,
        )
        Task.objects.create(user=self.user, title='Закрытая задача', status=Task.STATUS_DONE)

    def test_user_can_search_tasks(self):
        response = self.client.get(reverse('tasks:dashboard'), {'q': 'отчет'})

        self.assertContains(response, 'Учебный отчет')
        self.assertNotContains(response, 'Купить продукты')

    def test_user_can_filter_tasks_by_status(self):
        response = self.client.get(reverse('tasks:dashboard'), {'status': Task.STATUS_DONE})

        self.assertContains(response, 'Закрытая задача')
        self.assertNotContains(response, 'Учебный отчет')

    def test_dashboard_shows_task_statistics(self):
        response = self.client.get(reverse('tasks:dashboard'))

        self.assertEqual(response.context['stats']['total'], 3)
        self.assertEqual(response.context['stats']['new'], 1)
        self.assertEqual(response.context['stats']['in_progress'], 1)
        self.assertEqual(response.context['stats']['done'], 1)
