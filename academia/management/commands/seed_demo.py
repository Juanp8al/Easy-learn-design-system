"""
Datos de prueba institucionales: período, carreras, cursos, usuarios y matrículas.
Ejecutar: python manage.py seed_demo
Luego: python manage.py seed_classroom --weeks 1
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone
from academia.models import AcademicPeriod, Enrollment, Offering, Program
from accounts.models import Profile, Student


class Command(BaseCommand):
    help = "Crea período actual, 2 cursos ofertados, docente, estudiantes matriculados y usuarios demo."

    def handle(self, *args, **options):
        User = get_user_model()

        program, _ = Program.objects.get_or_create(
            slug="ingenieria-sistemas",
            defaults={
                "name": "Ingeniería de Sistemas",
                "code": "IS",
            },
        )

        period, created_period = AcademicPeriod.objects.get_or_create(
            name="2026-1",
            defaults={
                "starts_on": date(2026, 1, 15),
                "ends_on": date(2026, 6, 30),
                "is_current": True,
            },
        )
        if not created_period and not period.is_current:
            period.is_current = True
            period.save()

        admin_user, _ = User.objects.get_or_create(
            username="admin.demo",
            defaults={
                "first_name": "Ana",
                "last_name": "Administradora",
                "email": "admin.demo@easylearn.local",
                "role": Student.Role.ADMIN,
                "is_staff": True,
            },
        )
        if not admin_user.has_usable_password():
            admin_user.set_password("demo1234")
            admin_user.save()
        Profile.objects.get_or_create(student=admin_user)

        teacher, _ = User.objects.get_or_create(
            username="prof.demo",
            defaults={
                "first_name": "Carlos",
                "last_name": "Docente",
                "email": "prof.demo@easylearn.local",
                "role": Student.Role.TEACHER,
            },
        )
        if not teacher.has_usable_password():
            teacher.set_password("demo1234")
            teacher.save()
        Profile.objects.get_or_create(student=teacher)

        students = []
        for i, (uname, fname) in enumerate(
            [("estudiante1", "Laura"), ("estudiante2", "Miguel")], start=1
        ):
            st, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    "first_name": fname,
                    "last_name": "Pérez",
                    "email": f"{uname}@easylearn.local",
                    "role": Student.Role.STUDENT,
                    "academic_program": program,
                    "academic_semester": 5,
                },
            )
            if not st.has_usable_password():
                st.set_password("demo1234")
                st.save()
            if not st.academic_program_id:
                st.academic_program = program
                st.academic_semester = 5
                st.save(update_fields=["academic_program", "academic_semester"])
            Profile.objects.get_or_create(student=st)
            students.append(st)

        offerings_data = [
            ("IHC", "Interacción Humano-Computador", "A"),
            ("BD1", "Bases de Datos I", "A"),
        ]
        offerings = []
        for code, name, group in offerings_data:
            off, _ = Offering.objects.get_or_create(
                program=program,
                period=period,
                code=code,
                group=group,
                defaults={
                    "name": name,
                    "semester": 5,
                    "credits": 3,
                    "teacher": teacher,
                },
            )
            if not off.teacher_id:
                off.teacher = teacher
                off.save(update_fields=["teacher"])
            offerings.append(off)

        for st in students:
            for off in offerings:
                Enrollment.objects.get_or_create(
                    student=st,
                    offering=off,
                    defaults={"status": Enrollment.Status.ACTIVE},
                )

        self.stdout.write(self.style.SUCCESS("Usuarios demo (contraseña: demo1234):"))
        self.stdout.write("  admin.demo · prof.demo · estudiante1 · estudiante2")

        call_command("seed_classroom", weeks=1, force=True)

        self.stdout.write(self.style.SUCCESS("Datos de prueba listos."))
