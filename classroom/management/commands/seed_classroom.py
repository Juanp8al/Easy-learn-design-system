from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from academia.models import Enrollment, Offering
from classroom.models import (
    AcademicWeek,
    Activity,
    Announcement,
    Forum,
    Grade,
    StudyMaterial,
    Submission,
)

WEEK_TOPICS = [
    "Introducción y fundamentos",
    "Conceptos clave",
    "Práctica guiada",
    "Aplicación en contexto",
    "Evaluación y cierre",
]

PRIMARY_STUDENT_USERNAME = "estudiante_demo"
UNGRADED_DEMO_STUDENT = PRIMARY_STUDENT_USERNAME


class Command(BaseCommand):
    help = "Crea semanas, materiales y actividades de demostración para offerings existentes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--offering-code",
            type=str,
            default="",
            help="Solo sembrar un offering por código (ej. IHC).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recrear contenido si el offering ya tiene semanas.",
        )
        parser.add_argument(
            "--weeks",
            type=int,
            default=5,
            help="Número de semanas a crear por curso (por defecto 5).",
        )

    def handle(self, *args, **options):
        qs = Offering.objects.select_related("teacher", "period")
        if options["offering_code"]:
            qs = qs.filter(code__iexact=options["offering_code"].strip())
        if not qs.exists():
            self.stdout.write(self.style.WARNING("No hay offerings que coincidan."))
            return

        now = timezone.now()
        created_weeks = 0
        for offering in qs:
            if offering.academic_weeks.exists() and not options["force"]:
                self.stdout.write(f"  Omitido {offering.code}: ya tiene semanas.")
                continue
            if options["force"]:
                offering.academic_weeks.all().delete()

            week_topics = WEEK_TOPICS[: max(1, options["weeks"])]
            weeks = []
            for i, topic in enumerate(week_topics, start=1):
                last_n = len(week_topics)
                status = AcademicWeek.Status.COMPLETED if i < last_n - 1 else AcademicWeek.Status.IN_PROGRESS
                if i == last_n:
                    status = AcademicWeek.Status.IN_PROGRESS
                week = AcademicWeek.objects.create(
                    offering=offering,
                    week_number=i,
                    title=topic,
                    description=f"Contenidos de la semana {i} — {offering.name}.",
                    status=status,
                )
                weeks.append(week)
                created_weeks += 1

                StudyMaterial.objects.get_or_create(
                    week=week,
                    title=f"Lectura semana {i}",
                    defaults={
                        "description": "Documento base de la semana (demo).",
                        "material_type": StudyMaterial.MaterialType.DOCUMENT,
                        "external_url": "https://example.com/material",
                        "created_by": offering.teacher,
                    },
                )
                StudyMaterial.objects.get_or_create(
                    week=week,
                    title=f"Video complementario · semana {i}",
                    defaults={
                        "description": "Clase grabada y enlaces de apoyo.",
                        "material_type": StudyMaterial.MaterialType.VIDEO,
                        "external_url": "https://example.com/video",
                        "is_required": i <= 2,
                        "created_by": offering.teacher,
                    },
                )

                Forum.objects.get_or_create(
                    week=week,
                    title=f"Foro de discusión · semana {i}",
                    defaults={
                        "description": "Espacio para preguntas y debate sobre los contenidos de la semana.",
                        "status": Forum.Status.OPEN if i >= last_n - 1 else Forum.Status.CLOSED,
                        "created_by": offering.teacher,
                    },
                )

                due_offset = 8 - i
                Activity.objects.get_or_create(
                    week=week,
                    title=f"Tarea semana {i} · {offering.code}",
                    defaults={
                        "description": f"Entrega formativa de la semana {i}.",
                        "instructions": "Adjunte PDF o enlace según indique el docente.",
                        "activity_type": Activity.ActivityType.TASK,
                        "due_at": now + timedelta(days=due_offset),
                        "status": Activity.Status.PUBLISHED,
                        "allows_draft": True,
                        "created_by": offering.teacher,
                    },
                )
                if i % 2 == 0:
                    Activity.objects.get_or_create(
                        week=week,
                        title=f"Quiz semana {i}",
                        defaults={
                            "activity_type": Activity.ActivityType.QUIZ,
                            "due_at": now + timedelta(days=due_offset - 1),
                            "status": Activity.Status.PUBLISHED,
                            "allows_draft": False,
                            "created_by": offering.teacher,
                        },
                    )

            week_last = weeks[-1]
            task, _ = Activity.objects.get_or_create(
                week=week_last,
                title="Ensayo · principios de UX",
                defaults={
                    "description": "Análisis breve de principios de diseño centrado en el usuario.",
                    "instructions": "Redacte 800–1200 palabras y adjunte PDF o documento.",
                    "activity_type": Activity.ActivityType.TASK,
                    "due_at": now + timedelta(days=2),
                    "status": Activity.Status.PUBLISHED,
                    "allows_draft": True,
                    "created_by": offering.teacher,
                },
            )
            Activity.objects.get_or_create(
                week=week_last,
                title="Quiz · evaluación heurística",
                defaults={
                    "activity_type": Activity.ActivityType.QUIZ,
                    "due_at": now - timedelta(days=1),
                    "status": Activity.Status.PUBLISHED,
                    "allows_draft": False,
                    "created_by": offering.teacher,
                },
            )

            Announcement.objects.get_or_create(
                offering=offering,
                week=week_last,
                title=f"Recordatorio semana {week_last.week_number}",
                defaults={
                    "content": "Revise el material y complete las actividades antes de la fecha límite.",
                    "priority": Announcement.Priority.HIGH,
                    "author": offering.teacher,
                },
            )

            enrollments = Enrollment.objects.filter(
                offering=offering,
                status=Enrollment.Status.ACTIVE,
            ).select_related("student")

            for enrollment in enrollments:
                sub, created = Submission.objects.get_or_create(
                    activity=task,
                    student=enrollment.student,
                    defaults={
                        "comment": "Entrega de demostración.",
                        "is_draft": False,
                        "submitted_at": now - timedelta(hours=5),
                        "status": Submission.Status.SUBMITTED,
                    },
                )
                if not created and sub.is_draft:
                    sub.is_draft = False
                    sub.submitted_at = now - timedelta(hours=5)
                    sub.status = Submission.Status.SUBMITTED
                    sub.save()

                if enrollment.student.username != UNGRADED_DEMO_STUDENT:
                    Grade.objects.get_or_create(
                        submission=sub,
                        defaults={
                            "score": Decimal("4.2"),
                            "feedback": "Entrega revisada en datos de demostración.",
                            "graded_by": offering.teacher,
                        },
                    )
                    if sub.grade:
                        sub.status = Submission.Status.GRADED
                        sub.save(update_fields=["status"])

            first_week_task = (
                Activity.objects.filter(week=weeks[0], activity_type=Activity.ActivityType.TASK)
                .order_by("id")
                .first()
            )
            demo_enrollment = enrollments.filter(
                student__username=PRIMARY_STUDENT_USERNAME
            ).first()
            if first_week_task and demo_enrollment:
                sub_old, created_old = Submission.objects.get_or_create(
                    activity=first_week_task,
                    student=demo_enrollment.student,
                    defaults={
                        "comment": "Entrega calificada — semana 1.",
                        "is_draft": False,
                        "submitted_at": now - timedelta(days=12),
                        "status": Submission.Status.GRADED,
                    },
                )
                Grade.objects.get_or_create(
                    submission=sub_old,
                    defaults={
                        "score": Decimal("4.5"),
                        "feedback": "Excelente análisis introductorio.",
                        "graded_by": offering.teacher,
                    },
                )
                if created_old or not sub_old.grade_id:
                    sub_old.status = Submission.Status.GRADED
                    sub_old.save(update_fields=["status"])

            self.stdout.write(self.style.SUCCESS(f"  Aula lista: {offering.code} ({len(weeks)} semanas)"))

        self.stdout.write(self.style.SUCCESS(f"Semanas creadas: {created_weeks}"))
