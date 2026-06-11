from django.test import TestCase

from activity.models import ActionLog
from activity.services import log_action


class ActivityServiceTests(TestCase):
    def test_log_action_allows_missing_user(self):
        log_action(None, ActionLog.ACTION_LOGOUT, 'Анонимный выход.')

        log = ActionLog.objects.get()
        self.assertIsNone(log.user)
        self.assertEqual(log.action_type, ActionLog.ACTION_LOGOUT)
