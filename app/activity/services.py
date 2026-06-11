from .models import ActionLog


def log_action(user, action_type, description=''):
    ActionLog.objects.create(
        user=user if getattr(user, 'is_authenticated', False) else None,
        action_type=action_type,
        description=description,
    )
