from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from tasks.forms import TaskForm
from tasks.models import Task


class TaskFormTests(TestCase):
    def test_task_form_accepts_valid_data(self):
        future_date = (timezone.localdate() + timedelta(days=7)).isoformat()
        form = TaskForm(
            data={
                'title': 'Подготовить отчет',
                'description': 'Учебная практика',
                'status': Task.STATUS_IN_PROGRESS,
                'due_date': future_date,
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

    def test_task_form_rejects_blank_spaces_title(self):
        form = TaskForm(
            data={
                'title': '   ',
                'description': '',
                'status': Task.STATUS_NEW,
                'due_date': '',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('Введите название задачи.', form.errors['title'])

    def test_task_form_rejects_too_short_title(self):
        form = TaskForm(
            data={
                'title': 'A',
                'description': '',
                'status': Task.STATUS_NEW,
                'due_date': '',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('Название должно быть не короче 3 символов.', form.errors['title'])

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

    def test_task_form_rejects_past_due_date(self):
        past_date = (timezone.localdate() - timedelta(days=1)).isoformat()
        form = TaskForm(
            data={
                'title': 'Проверить дату',
                'description': '',
                'status': Task.STATUS_NEW,
                'due_date': past_date,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('Срок задачи не может быть в прошлом.', form.errors['due_date'])
