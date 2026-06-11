from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tasks.models import Task


class TasksFrontendTests(TestCase):
    def setUp(self):
        self.future_date = timezone.localdate() + timedelta(days=7)
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
            due_date=self.future_date,
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
        self.assertContains(response, self.future_date.strftime('%d.%m.%Y'))
        self.assertContains(response, 'status-in_progress')

    def test_task_create_page_renders_form_controls(self):
        response = self.client.get(reverse('tasks:task_create'))

        self.assertContains(response, 'Новая задача')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="due_date"')
        self.assertContains(response, 'type="date"')
        self.assertContains(response, 'Например: подготовить отчет')
        self.assertContains(response, 'Кратко опишите детали задачи')
        self.assertContains(response, reverse('tasks:dashboard'))

    def test_task_create_page_renders_validation_errors(self):
        response = self.client.post(
            reverse('tasks:task_create'),
            {
                'title': ' ',
                'description': '',
                'status': Task.STATUS_NEW,
                'due_date': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Введите название задачи.')

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
        self.assertIn('.pagination', css)
        self.assertIn('.pagination-status', css)

    def test_js_file_exists_and_contains_form_helpers(self):
        js_path = finders.find('js/app.js')

        self.assertIsNotNone(js_path)
        with open(js_path, encoding='utf-8') as js_file:
            js = js_file.read()

        self.assertIn('status-form', js)
        self.assertIn('is-submitting', js)
        self.assertIn('message-close', js)
