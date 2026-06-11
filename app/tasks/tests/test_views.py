from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tasks.models import Task


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
        future_date = (timezone.localdate() + timedelta(days=7)).isoformat()
        response = self.client.post(
            reverse('tasks:task_create'),
            {
                'title': 'Подготовить README',
                'description': 'Описать запуск проекта',
                'status': Task.STATUS_NEW,
                'due_date': future_date,
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

    def test_invalid_status_does_not_change_task(self):
        task = Task.objects.create(user=self.user, title='Не менять статус', status=Task.STATUS_NEW)

        response = self.client.post(
            reverse('tasks:task_status', args=(task.pk,)),
            {'status': 'broken'},
            follow=True,
        )

        task.refresh_from_db()
        self.assertEqual(task.status, Task.STATUS_NEW)
        self.assertContains(response, 'Некорректный статус задачи.')
        self.assertContains(response, 'message-error')

    def test_user_cannot_update_another_user_task(self):
        other = User.objects.create_user(username='other', password='StrongPass12345')
        task = Task.objects.create(user=other, title='Чужая задача')

        response = self.client.get(reverse('tasks:task_update', args=(task.pk,)))

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_another_user_task(self):
        other = User.objects.create_user(username='other', password='StrongPass12345')
        task = Task.objects.create(user=other, title='Чужая задача')

        response = self.client.post(reverse('tasks:task_delete', args=(task.pk,)))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_user_cannot_change_status_of_another_user_task(self):
        other = User.objects.create_user(username='other', password='StrongPass12345')
        task = Task.objects.create(user=other, title='Чужая задача', status=Task.STATUS_NEW)

        response = self.client.post(
            reverse('tasks:task_status', args=(task.pk,)),
            {'status': Task.STATUS_DONE},
        )

        task.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(task.status, Task.STATUS_NEW)

    def test_anonymous_user_is_redirected_from_task_create(self):
        self.client.logout()

        response = self.client.get(reverse('tasks:task_create'))

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('tasks:task_create')}")

    def test_anonymous_user_is_redirected_from_task_update(self):
        task = Task.objects.create(user=self.user, title='Закрытая задача')
        self.client.logout()

        response = self.client.get(reverse('tasks:task_update', args=(task.pk,)))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('tasks:task_update', args=(task.pk,))}",
        )

    def test_anonymous_user_is_redirected_from_task_delete(self):
        task = Task.objects.create(user=self.user, title='Закрытая задача')
        self.client.logout()

        response = self.client.post(reverse('tasks:task_delete', args=(task.pk,)))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('tasks:task_delete', args=(task.pk,))}",
        )
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_anonymous_user_is_redirected_from_status_change(self):
        task = Task.objects.create(user=self.user, title='Закрытая задача', status=Task.STATUS_NEW)
        self.client.logout()

        response = self.client.post(
            reverse('tasks:task_status', args=(task.pk,)),
            {'status': Task.STATUS_DONE},
        )

        task.refresh_from_db()
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('tasks:task_status', args=(task.pk,))}",
        )
        self.assertEqual(task.status, Task.STATUS_NEW)


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

    def test_search_looks_in_description(self):
        response = self.client.get(reverse('tasks:dashboard'), {'q': 'документацию'})

        self.assertContains(response, 'Учебный отчет')
        self.assertNotContains(response, 'Купить продукты')

    def test_unknown_status_filter_is_ignored(self):
        response = self.client.get(reverse('tasks:dashboard'), {'status': 'unknown'})

        self.assertEqual(len(response.context['tasks']), 3)


class TaskPaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='StrongPass12345')
        self.client.force_login(self.user)

    def create_tasks(self, count, title_prefix='Задача', status=Task.STATUS_NEW):
        for index in range(count):
            Task.objects.create(
                user=self.user,
                title=f'{title_prefix} {index + 1}',
                status=status,
            )

    def test_dashboard_shows_limited_tasks_on_first_page(self):
        self.create_tasks(8)

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertEqual(len(response.context['tasks']), 6)
        self.assertTrue(response.context['is_paginated'])
        self.assertContains(response, 'Страница 1 из 2')
        self.assertContains(response, 'Вперед')

    def test_dashboard_shows_remaining_tasks_on_second_page(self):
        self.create_tasks(8)

        response = self.client.get(reverse('tasks:dashboard'), {'page': 2})

        self.assertEqual(len(response.context['tasks']), 2)
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertFalse(response.context['page_obj'].has_next())
        self.assertContains(response, 'Страница 2 из 2')

    def test_pagination_keeps_search_and_status_filters(self):
        self.create_tasks(7, title_prefix='project', status=Task.STATUS_NEW)
        Task.objects.create(user=self.user, title='project done', status=Task.STATUS_DONE)

        response = self.client.get(
            reverse('tasks:dashboard'),
            {'q': 'project', 'status': Task.STATUS_NEW},
        )

        self.assertEqual(response.context['page_query'], 'q=project&status=new')
        self.assertContains(response, '?q=project&amp;status=new&amp;page=2')

    def test_page_out_of_range_uses_last_page(self):
        self.create_tasks(8)

        response = self.client.get(reverse('tasks:dashboard'), {'page': 99})

        self.assertEqual(response.context['page_obj'].number, 2)
