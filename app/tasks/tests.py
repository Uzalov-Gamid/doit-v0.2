from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.test import TestCase
from django.urls import reverse

from .forms import TaskForm
from .models import Task


class TaskModelTests(TestCase):
    def test_task_has_default_status_and_string_title(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        task = Task.objects.create(user=user, title='Проверить модель')

        self.assertEqual(task.status, Task.STATUS_NEW)
        self.assertEqual(str(task), 'Проверить модель')
        self.assertEqual(task.get_status_display(), 'Новая')

    def test_tasks_are_ordered_by_newest_first(self):
        user = User.objects.create_user(username='student', password='StrongPass12345')
        old_task = Task.objects.create(user=user, title='Старая задача')
        new_task = Task.objects.create(user=user, title='Новая задача')

        self.assertEqual(list(Task.objects.all()), [new_task, old_task])


class TaskFormTests(TestCase):
    def test_task_form_accepts_valid_data(self):
        form = TaskForm(
            data={
                'title': 'Подготовить отчет',
                'description': 'Учебная практика',
                'status': Task.STATUS_IN_PROGRESS,
                'due_date': '2026-06-20',
            }
        )

        self.assertTrue(form.is_valid())

    def test_task_form_requires_title(self):
        form = TaskForm(
            data={
                'title': '',
                'description': 'Без названия',
                'status': Task.STATUS_NEW,
                'due_date': '',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_task_form_rejects_unknown_status(self):
        form = TaskForm(
            data={
                'title': 'Некорректный статус',
                'description': '',
                'status': 'unknown',
                'due_date': '',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)


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


class TasksFrontendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass12345',
        )
        self.client.force_login(self.user)
        self.task = Task.objects.create(
            user=self.user,
            title='Frontend задача',
            description='Проверить HTML интерфейса',
            status=Task.STATUS_IN_PROGRESS,
            due_date='2026-06-20',
        )

    def test_dashboard_renders_navigation_profile_filters_and_actions(self):
        response = self.client.get(reverse('tasks:dashboard'))

        self.assertContains(response, 'Личный кабинет')
        self.assertContains(response, 'student@example.com')
        self.assertContains(response, 'name="q"')
        self.assertContains(response, 'name="status"')
        self.assertContains(response, reverse('tasks:task_create'))
        self.assertContains(response, reverse('tasks:task_update', args=(self.task.pk,)))
        self.assertContains(response, reverse('tasks:task_delete', args=(self.task.pk,)))
        self.assertContains(response, reverse('tasks:task_status', args=(self.task.pk,)))

    def test_dashboard_empty_state_without_tasks_has_primary_action(self):
        Task.objects.all().delete()

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertContains(response, 'Начало работы')
        self.assertContains(response, 'Задач пока нет')
        self.assertContains(response, 'Создать первую задачу')
        self.assertContains(response, reverse('tasks:task_create'))

    def test_dashboard_empty_state_for_filtered_results_has_reset_action(self):
        response = self.client.get(reverse('tasks:dashboard'), {'q': 'нет такого текста'})

        self.assertContains(response, 'Ничего не найдено')
        self.assertContains(response, 'Нет задач по выбранным условиям')
        self.assertContains(response, 'Сбросить фильтры')
        self.assertContains(response, reverse('tasks:dashboard'))

    def test_dashboard_renders_task_status_and_due_date(self):
        response = self.client.get(reverse('tasks:dashboard'))

        self.assertContains(response, 'Frontend задача')
        self.assertContains(response, 'В работе')
        self.assertContains(response, '20.06.2026')
        self.assertContains(response, 'status-in_progress')

    def test_task_create_page_renders_form_controls(self):
        response = self.client.get(reverse('tasks:task_create'))

        self.assertContains(response, 'Новая задача')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="due_date"')
        self.assertContains(response, 'type="date"')
        self.assertContains(response, reverse('tasks:dashboard'))

    def test_task_update_page_renders_existing_values(self):
        response = self.client.get(reverse('tasks:task_update', args=(self.task.pk,)))

        self.assertContains(response, 'Редактирование задачи')
        self.assertContains(response, 'Frontend задача')
        self.assertContains(response, 'Проверить HTML интерфейса')

    def test_delete_page_renders_confirmation(self):
        response = self.client.get(reverse('tasks:task_delete', args=(self.task.pk,)))

        self.assertContains(response, 'Удаление задачи')
        self.assertContains(response, 'Frontend задача')
        self.assertContains(response, 'Удалить')

    def test_success_message_renders_after_task_create(self):
        response = self.client.post(
            reverse('tasks:task_create'),
            {
                'title': 'Сообщение успеха',
                'description': '',
                'status': Task.STATUS_NEW,
                'due_date': '',
            },
            follow=True,
        )

        self.assertContains(response, 'Задача создана.')
        self.assertContains(response, 'message-success')
        self.assertContains(response, 'message-close')


class StaticFrontendTests(SimpleTestCase):
    def test_css_file_exists_and_contains_responsive_rules(self):
        css_path = finders.find('css/styles.css')

        self.assertIsNotNone(css_path)
        with open(css_path, encoding='utf-8') as css_file:
            css = css_file.read()

        self.assertIn('@media (max-width: 640px)', css)
        self.assertIn('.dashboard', css)
        self.assertIn('.task-card', css)
        self.assertIn('.empty-state-action', css)
        self.assertIn('.empty-actions', css)
        self.assertIn('.filter-field', css)
        self.assertIn('.message-error', css)

    def test_js_file_exists_and_contains_form_helpers(self):
        js_path = finders.find('js/app.js')

        self.assertIsNotNone(js_path)
        with open(js_path, encoding='utf-8') as js_file:
            js = js_file.read()

        self.assertIn('status-form', js)
        self.assertIn('is-submitting', js)
        self.assertIn('message-close', js)
