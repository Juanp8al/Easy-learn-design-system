from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from academia.models import AcademicPeriod, Enrollment, Offering, Program
from accounts.models import Profile, Student
from classroom.models import AcademicWeek, Activity, Grade, Submission


class ClassroomFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.program = Program.objects.create(name="IS", code="IS", slug="is")
        self.period = AcademicPeriod.objects.create(name="2026-1", is_current=True)
        self.teacher = User.objects.create_user(
            username="prof.test",
            password="demo1234",
            role=Student.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username="est.test",
            password="demo1234",
            role=Student.Role.STUDENT,
            academic_program=self.program,
        )
        Profile.objects.get_or_create(student=self.student)
        self.offering = Offering.objects.create(
            program=self.program,
            period=self.period,
            name="Prueba",
            code="TST",
            teacher=self.teacher,
        )
        Enrollment.objects.create(
            student=self.student,
            offering=self.offering,
            status=Enrollment.Status.ACTIVE,
        )
        self.week = AcademicWeek.objects.create(
            offering=self.offering,
            week_number=1,
            title="Semana 1",
        )
        self.activity = Activity.objects.create(
            week=self.week,
            title="Actividad",
            status=Activity.Status.PUBLISHED,
        )

    def test_student_course_list_requires_enrollment(self):
        self.client.login(username="est.test", password="demo1234")
        resp = self.client.get(reverse("classroom:course_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "TST")

    def test_teacher_cannot_access_student_only_dashboard(self):
        self.client.login(username="prof.test", password="demo1234")
        resp = self.client.get(reverse("notes:dashboard"))
        self.assertEqual(resp.status_code, 302)

    def test_grade_creates_notification(self):
        from accounts.models import UserNotification

        sub = Submission.objects.create(
            activity=self.activity,
            student=self.student,
            is_draft=False,
            status=Submission.Status.SUBMITTED,
        )
        Grade.objects.create(
            submission=sub,
            score=Decimal("4.0"),
            graded_by=self.teacher,
        )
        self.assertTrue(
            UserNotification.objects.filter(
                user=self.student,
                kind=UserNotification.Kind.GRADE,
            ).exists()
        )
