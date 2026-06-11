from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import ActionLog
from .services import log_action


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_action(user, ActionLog.ACTION_LOGIN, 'Пользователь вошел в систему.')


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_action(user, ActionLog.ACTION_LOGOUT, 'Пользователь вышел из системы.')
