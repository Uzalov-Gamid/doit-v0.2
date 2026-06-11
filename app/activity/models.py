from django.conf import settings
from django.db import models


class ActionLog(models.Model):
    ACTION_REGISTER = 'register'
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_TASK_CREATE = 'task_create'
    ACTION_TASK_UPDATE = 'task_update'
    ACTION_TASK_DELETE = 'task_delete'
    ACTION_STATUS_CHANGE = 'status_change'

    ACTION_CHOICES = (
        (ACTION_REGISTER, 'Регистрация'),
        (ACTION_LOGIN, 'Вход'),
        (ACTION_LOGOUT, 'Выход'),
        (ACTION_TASK_CREATE, 'Создание задачи'),
        (ACTION_TASK_UPDATE, 'Редактирование задачи'),
        (ACTION_TASK_DELETE, 'Удаление задачи'),
        (ACTION_STATUS_CHANGE, 'Изменение статуса'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='action_logs',
        verbose_name='Пользователь',
    )
    action_type = models.CharField('Тип действия', max_length=32, choices=ACTION_CHOICES)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Запись журнала'
        verbose_name_plural = 'Журнал действий'

    def __str__(self):
        username = self.user.username if self.user else 'deleted-user'
        return f'{username}: {self.get_action_type_display()}'
