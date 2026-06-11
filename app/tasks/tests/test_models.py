from django.contrib.auth.models import User
from django.test import TestCase

from tasks.models import Task


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
