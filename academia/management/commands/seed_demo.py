"""
Simulación institucional completa para presentación EasyLearn.

Ejecutar: python manage.py seed_demo

Cuentas (contraseña para todas): EasyLearn_Demo_2026
  estudiante_demo · docente_demo · admin_demo
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from academia.models import AcademicPeriod, Enrollment, Offering, Program
from accounts.models import Profile, Student
from classroom.models import Announcement
from notes.models import Course, Entry, SubTopic, Topic
from revision.models import Objective

DEMO_PASSWORD = "EasyLearn_Demo_2026"
PRIMARY_STUDENT_USERNAME = "estudiante_demo"


def _upsert_user(
    User,
    *,
    username,
    role,
    first_name,
    last_name,
    email,
    program=None,
    semester=None,
):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
        },
    )
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.role = role
    user.is_active = True
    if program is not None:
        user.academic_program = program
    if semester is not None:
        user.academic_semester = semester
    user.set_password(DEMO_PASSWORD)
    user.save()
    Profile.objects.get_or_create(student=user)
    return user


def _seed_student_workspace(student):
    """Apuntes y objetivos de repaso personal (pestaña Repaso del portal)."""
    today = timezone.localdate()

    course_specs = [
        (
            "Repaso · Interacción Humano-Computador",
            "IHC-R",
            "Apuntes y mapas conceptuales de IHC para el parcial.",
        ),
        (
            "Repaso · Bases de Datos",
            "BD1-R",
            "Modelo relacional, normalización y consultas SQL.",
        ),
    ]
    courses = []
    for name, code, about in course_specs:
        course, _ = Course.objects.get_or_create(
            student=student,
            course_code=code,
            defaults={
                "name": name,
                "about": about,
                "course_type": Course.CourseType.COURSEWORK,
            },
        )
        course.name = name
        course.about = about
        course.save(update_fields=["name", "about"])
        courses.append(course)

    topic_specs = [
        (1, "Usabilidad y experiencia de usuario", "Heurísticas de Nielsen y pruebas con usuarios."),
        (2, "Accesibilidad web", "WCAG, contraste y navegación por teclado."),
        (3, "Modelo entidad-relación", "Cardinalidad, claves y diagramas."),
    ]
    for course in courses[:1]:
        for num, tname, overview in topic_specs[:2]:
            topic, _ = Topic.objects.get_or_create(
                course=course,
                number=num,
                defaults={"name": tname, "overview": overview},
            )
            topic.name = tname
            topic.overview = overview
            topic.save(update_fields=["name", "overview"])
            sub, _ = SubTopic.objects.get_or_create(
                topic=topic,
                number=1,
                defaults={"name": f"Resumen {tname[:24]}"},
            )
            Entry.objects.get_or_create(
                subtopic=sub,
                name=f"Apunte · {tname[:32]}",
                defaults={
                    "content": (
                        f"Notas de estudio generadas para la demo.\n\n"
                        f"- {overview}\n"
                        f"- Fecha: {today.isoformat()}"
                    ),
                    "revised": num == 1,
                },
            )

    if courses:
        Objective.objects.get_or_create(
            course=courses[0],
            name="Preparar ensayo de UX",
            defaults={
                "start_date": today - timedelta(days=3),
                "end_date": today + timedelta(days=10),
                "description": "Borrador del ensayo y revisión con el checklist del docente.",
                "complete": False,
            },
        )
        Objective.objects.get_or_create(
            course=courses[0],
            name="Repasar heurísticas (vencido demo)",
            defaults={
                "start_date": today - timedelta(days=14),
                "end_date": today - timedelta(days=2),
                "description": "Objetivo vencido para mostrar alertas en Repaso.",
                "complete": False,
            },
        )
        if len(courses) > 1:
            Objective.objects.get_or_create(
                course=courses[1],
                name="Práctica SQL semana 3",
                defaults={
                    "start_date": today,
                    "end_date": today + timedelta(days=5),
                    "description": "Ejercicios de JOIN y agregación.",
                    "complete": False,
                },
            )


def _seed_announcements(teacher, offerings):
    """Avisos para Mensajes / tablero estudiante."""
    now = timezone.now()
    samples = [
        (
            "Bienvenida al período 2026-1",
            "Revise el cronograma de cada asignatura y las fechas de entrega en el aula virtual.",
            Announcement.Priority.HIGH,
        ),
        (
            "Taller de repaso — semana 2",
            "Sesión síncrona el viernes 10:00. Traiga dudas sobre el material publicado.",
            Announcement.Priority.NORMAL,
        ),
        (
            "Recordatorio de entrega",
            "Las actividades con fecha límite esta semana deben subirse antes de las 23:59.",
            Announcement.Priority.HIGH,
        ),
        (
            "Foro de consultas abierto",
            "Use el foro de la semana en curso para preguntas técnicas; evite correos individuales.",
            Announcement.Priority.NORMAL,
        ),
    ]
    for off in offerings:
        for idx, (title, content, priority) in enumerate(samples):
            key_title = f"{title} · {off.code}"
            Announcement.objects.get_or_create(
                offering=off,
                title=key_title,
                defaults={
                    "content": content,
                    "priority": priority,
                    "author": teacher,
                    "published_at": now - timedelta(days=idx + 1, hours=idx * 2),
                },
            )


class Command(BaseCommand):
    help = (
        "Crea simulación completa: períodos, carreras, cursos, matrículas, aula y cuentas demo "
        f"({PRIMARY_STUDENT_USERNAME}, docente_demo, admin_demo)."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        program_is, _ = Program.objects.get_or_create(
            slug="ingenieria-sistemas",
            defaults={"name": "Ingeniería de Sistemas", "code": "IS"},
        )
        program_ii, _ = Program.objects.get_or_create(
            slug="ingenieria-industrial",
            defaults={"name": "Ingeniería Industrial", "code": "II"},
        )

        period_prev, _ = AcademicPeriod.objects.get_or_create(
            name="2025-2",
            defaults={
                "starts_on": date(2025, 8, 1),
                "ends_on": date(2025, 12, 15),
                "is_current": False,
            },
        )
        period_prev.is_current = False
        period_prev.save(update_fields=["is_current"])

        period, _ = AcademicPeriod.objects.get_or_create(
            name="2026-1",
            defaults={
                "starts_on": date(2026, 1, 15),
                "ends_on": date(2026, 6, 30),
                "is_current": True,
            },
        )
        period.is_current = True
        period.save(update_fields=["is_current"])

        AcademicPeriod.objects.get_or_create(
            name="2026-2",
            defaults={
                "starts_on": date(2026, 7, 1),
                "ends_on": date(2026, 12, 15),
                "is_current": False,
            },
        )

        admin_user = _upsert_user(
            User,
            username="admin_demo",
            role=Student.Role.ADMIN,
            first_name="Andrea",
            last_name="Vega",
            email="admin_demo@easylearn.local",
        )

        teacher = _upsert_user(
            User,
            username="docente_demo",
            role=Student.Role.TEACHER,
            first_name="Carlos",
            last_name="Mendoza",
            email="docente_demo@easylearn.local",
        )

        demo_student = _upsert_user(
            User,
            username=PRIMARY_STUDENT_USERNAME,
            role=Student.Role.STUDENT,
            first_name="Laura",
            last_name="Ramírez",
            email="estudiante_demo@easylearn.local",
            program=program_is,
            semester=5,
        )

        extra_students = []
        for uname, fname, lname in [
            ("maria_demo", "María", "González"),
            ("juan_demo", "Juan", "Ruiz"),
            ("sofia_demo", "Sofía", "López"),
            ("diego_demo", "Diego", "Castro"),
        ]:
            st = _upsert_user(
                User,
                username=uname,
                role=Student.Role.STUDENT,
                first_name=fname,
                last_name=lname,
                email=f"{uname}@easylearn.local",
                program=program_is if uname != "sofia_demo" else program_ii,
                semester=4 if uname == "sofia_demo" else 5,
            )
            extra_students.append(st)

        all_students = [demo_student, *extra_students]

        offerings_data = [
            (program_is, "IHC", "Interacción Humano-Computador", "A", 5, 3),
            (program_is, "BD1", "Bases de Datos I", "A", 5, 3),
            (program_is, "ALG", "Algoritmos y estructuras de datos", "B", 5, 4),
            (program_is, "RED", "Redes de computadores", "A", 6, 3),
            (program_ii, "INV", "Investigación de operaciones", "A", 6, 3),
        ]
        offerings = []
        for prog, code, name, group, semester, credits in offerings_data:
            off, _ = Offering.objects.get_or_create(
                program=prog,
                period=period,
                code=code,
                group=group,
                defaults={
                    "name": name,
                    "semester": semester,
                    "credits": credits,
                    "teacher": teacher,
                },
            )
            off.name = name
            off.teacher = teacher
            off.semester = semester
            off.credits = credits
            off.save(update_fields=["name", "teacher", "semester", "credits"])
            offerings.append(off)

        for st in all_students:
            for off in offerings[:4] if st.username != "sofia_demo" else offerings[3:]:
                Enrollment.objects.get_or_create(
                    student=st,
                    offering=off,
                    defaults={"status": Enrollment.Status.ACTIVE},
                )

        Enrollment.objects.filter(
            student=extra_students[2],
            offering=offerings[4],
        ).update(status=Enrollment.Status.WITHDRAWN)

        _seed_student_workspace(demo_student)
        _seed_announcements(teacher, offerings)

        self.stdout.write(self.style.SUCCESS("Cuentas de demostración (contraseña única):"))
        self.stdout.write(f"  {DEMO_PASSWORD}")
        self.stdout.write("  estudiante_demo  -> /dashboard")
        self.stdout.write("  docente_demo     -> /accounts/panel/docente/")
        self.stdout.write("  admin_demo       -> /accounts/panel/administrador/")
        self.stdout.write("")
        self.stdout.write("Estudiantes adicionales (misma contraseña): maria_demo, juan_demo, sofia_demo, diego_demo")

        call_command("seed_classroom", weeks=5, force=True)

        self.stdout.write(self.style.SUCCESS("Simulación lista: tableros, aula, repaso, admin y mensajes."))
