from django.conf import settings
from django.db import models


class Task(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_DONE, 'Выполнена'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Пользователь',
    )
    title = models.CharField('Название', max_length=160)
    description = models.TextField('Описание', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    due_date = models.DateField('Срок', blank=True, null=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title
