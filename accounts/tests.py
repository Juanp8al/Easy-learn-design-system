from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

DEMO_PASSWORD = "EasyLearn_Demo_2026"


class PortalAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo")
        cls.User = get_user_model()

    def setUp(self):
        self.client = Client()

    def _login(self, username):
        user = self.User.objects.get(username=username)
        self.client.force_login(user)

    def test_student_profile_ok(self):
        self._login("estudiante_demo")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi perfil")

    def test_teacher_profile_ok(self):
        self._login("docente_demo")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_admin_profile_ok(self):
        self._login("admin_demo")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_teacher_dashboard_ok(self):
        self._login("docente_demo")
        response = self.client.get(reverse("dashboard_teacher"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "view-teacher-dashboard")

    def test_admin_dashboard_ok(self):
        self._login("admin_demo")
        response = self.client.get(reverse("dashboard_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "view-admin-dashboard")

    def test_student_dashboard_ok(self):
        self._login("estudiante_demo")
        response = self.client.get(reverse("notes:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "view-dashboard")

    def test_profile_password_change_form(self):
        self._login("estudiante_demo")
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "Cambiar contraseña")
        self.assertContains(response, "portal-password-dialog")
        self.assertContains(response, "data-portal-password-open")
        self.assertContains(response, "¿Desea cambiar su contraseña")
        self.assertNotContains(response, "Olvidó su contraseña")
        self.assertNotContains(response, 'id="cambiar-contraseña"')

    def test_profile_password_change_succeeds(self):
        user = self.User.objects.get(username="estudiante_demo")
        user.set_password(DEMO_PASSWORD)
        user.save(update_fields=["password"])
        self.assertTrue(
            self.client.login(username="estudiante_demo", password=DEMO_PASSWORD)
        )
        response = self.client.post(
            reverse("profile"),
            {
                "form_type": "password",
                "old_password": DEMO_PASSWORD,
                "new_password1": "PortalTest#2026Abc",
                "new_password2": "PortalTest#2026Abc",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "actualiz")
        user = self.User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password("PortalTest#2026Abc"))
        user.set_password(DEMO_PASSWORD)
        user.save()
