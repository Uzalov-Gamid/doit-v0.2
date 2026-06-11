import os
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from activity.models import ActionLog
from activity.services import log_action
from tasks.models import Task


class Command(BaseCommand):
    help = 'Create demo users, tasks, and action log records.'

    def add_arguments(self, parser):
        parser.add_argument('--user-password', default=os.getenv('DEMO_USER_PASSWORD', 'DemoUser12345'))
        parser.add_argument('--admin-password', default=os.getenv('DEMO_ADMIN_PASSWORD', 'DemoAdmin12345'))

    def handle(self, *args, **options):
        demo_user, _ = User.objects.update_or_create(
            username='demo_user',
            defaults={
                'email': 'demo_user@example.com',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
            },
        )
        demo_user.set_password(options['user_password'])
        demo_user.save()

        demo_admin, _ = User.objects.update_or_create(
            username='demo_admin',
            defaults={
                'email': 'demo_admin@example.com',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        demo_admin.set_password(options['admin_password'])
        demo_admin.save()

        today = timezone.localdate()
        demo_tasks = (
            {
                'title': 'Демо: подготовить отчет по практике',
                'description': 'Собрать описание функций, скриншоты и инструкцию запуска.',
                'status': Task.STATUS_IN_PROGRESS,
                'due_date': today + timedelta(days=3),
            },
            {
                'title': 'Демо: проверить Docker-запуск',
                'description': 'Запустить проект через Docker Compose и проверить миграции.',
                'status': Task.STATUS_NEW,
                'due_date': today + timedelta(days=5),
            },
            {
                'title': 'Демо: оформить список задач',
                'description': 'Проверить поиск, фильтр и пагинацию в личном кабинете.',
                'status': Task.STATUS_DONE,
                'due_date': today + timedelta(days=1),
            },
        )

        for task_data in demo_tasks:
            Task.objects.update_or_create(
                user=demo_user,
                title=task_data['title'],
                defaults=task_data,
            )

        ActionLog.objects.filter(description__startswith='Демо:').delete()
        log_action(demo_user, ActionLog.ACTION_REGISTER, 'Демо: пользователь создан для показа проекта.')
        log_action(demo_user, ActionLog.ACTION_LOGIN, 'Демо: пользователь вошел в систему.')
        log_action(demo_user, ActionLog.ACTION_TASK_CREATE, 'Демо: созданы задачи разных статусов.')
        log_action(demo_admin, ActionLog.ACTION_LOGIN, 'Демо: администратор открыл журнал действий.')

        self.stdout.write(self.style.SUCCESS('Demo data created.'))
        self.stdout.write('User: demo_user / password from DEMO_USER_PASSWORD or --user-password')
        self.stdout.write('Admin: demo_admin / password from DEMO_ADMIN_PASSWORD or --admin-password')
