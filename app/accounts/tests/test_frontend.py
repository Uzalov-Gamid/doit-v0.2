from django.test import TestCase
from django.urls import reverse


class AccountsFrontendTests(TestCase):
    def test_login_page_renders_expected_form_and_links(self):
        response = self.client.get(reverse('accounts:login'))

        self.assertContains(response, '<form method="post" class="form">')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, reverse('accounts:register'))
        self.assertContains(response, 'css/styles.css')
        self.assertContains(response, 'js/app.js')

    def test_register_page_renders_expected_form_fields(self):
        response = self.client.get(reverse('accounts:register'))

        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')
        self.assertContains(response, reverse('accounts:login'))
