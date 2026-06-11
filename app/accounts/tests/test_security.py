from django.conf import settings
from django.test import SimpleTestCase


class SecuritySettingsTests(SimpleTestCase):
    def test_auth_redirect_settings_are_configured(self):
        self.assertEqual(settings.LOGIN_URL, 'accounts:login')
        self.assertEqual(settings.LOGIN_REDIRECT_URL, 'tasks:dashboard')
        self.assertEqual(settings.LOGOUT_REDIRECT_URL, 'accounts:login')

    def test_cookie_security_defaults_are_enabled(self):
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(settings.CSRF_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, 'Lax')
        self.assertEqual(settings.CSRF_COOKIE_SAMESITE, 'Lax')
