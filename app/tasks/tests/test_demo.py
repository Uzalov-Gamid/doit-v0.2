from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from activity.models import ActionLog
from tasks.models import Task


class DemoDataCommandTests(TestCase):
    def test_seed_demo_data_creates_users_tasks_and_logs(self):
        output = StringIO()

        call_command('seed_demo_data', stdout=output)

        demo_user = User.objects.get(username='demo_user')
        demo_admin = User.objects.get(username='demo_admin')

        self.assertTrue(demo_user.check_password('DemoUser12345'))
        self.assertTrue(demo_admin.check_password('DemoAdmin12345'))
        self.assertTrue(demo_admin.is_staff)
        self.assertTrue(demo_admin.is_superuser)
        self.assertEqual(Task.objects.filter(user=demo_user).count(), 3)
        self.assertTrue(Task.objects.filter(user=demo_user, status=Task.STATUS_NEW).exists())
        self.assertTrue(Task.objects.filter(user=demo_user, status=Task.STATUS_IN_PROGRESS).exists())
        self.assertTrue(Task.objects.filter(user=demo_user, status=Task.STATUS_DONE).exists())
        self.assertEqual(ActionLog.objects.filter(description__startswith='Демо:').count(), 4)
        self.assertIn('Demo data created.', output.getvalue())

    def test_seed_demo_data_is_idempotent_for_tasks(self):
        call_command('seed_demo_data', stdout=StringIO())
        call_command('seed_demo_data', stdout=StringIO())

        demo_user = User.objects.get(username='demo_user')

        self.assertEqual(Task.objects.filter(user=demo_user).count(), 3)
        self.assertEqual(ActionLog.objects.filter(description__startswith='Демо:').count(), 4)
