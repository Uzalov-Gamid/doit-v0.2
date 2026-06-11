from django.test import SimpleTestCase


class DashboardSmokeTests(SimpleTestCase):
    def test_dashboard_route_exists(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
