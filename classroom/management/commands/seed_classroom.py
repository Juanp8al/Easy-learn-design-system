from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from academia.models import Enrollment, Offering
from classroom.models import (
    AcademicWeek,
    Activity,
    Announcement,
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
                status = AcademicWeek.Status.COMPLETED if i < last_n else AcademicWeek.Status.IN_PROGRESS
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
                        "description": "Material base de la semana.",
                        "material_type": StudyMaterial.MaterialType.DOCUMENT,
                        "external_url": "https://example.com/material",
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
            if len(weeks) >= 2:
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

            enrollment = (
                Enrollment.objects.filter(
                    offering=offering,
                    status=Enrollment.Status.ACTIVE,
                )
                .select_related("student")
                .first()
            )
            if enrollment:
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

                Grade.objects.get_or_create(
                    submission=sub,
                    defaults={
                        "score": Decimal("4.5"),
                        "feedback": "Buen análisis. Profundice en heurísticas de Nielsen.",
                        "graded_by": offering.teacher,
                    },
                )
                if sub.grade:
                    sub.status = Submission.Status.GRADED
                    sub.save(update_fields=["status"])

            self.stdout.write(self.style.SUCCESS(f"  Aula lista: {offering.code} ({len(weeks)} semanas)"))

        self.stdout.write(self.style.SUCCESS(f"Semanas creadas: {created_weeks}"))
