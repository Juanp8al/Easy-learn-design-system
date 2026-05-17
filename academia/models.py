"""
Modelo académico MER: Carrera → Curso (oferta) → Docente + Inscripción (estudiante).
El vínculo docente–estudiante es siempre a través del curso ofertado.
"""

from django.conf import settings
from django.db import models


class Program(models.Model):
    """Carrera o programa académico."""

    name = models.CharField("Nombre", max_length=200)
    code = models.CharField("Código", max_length=32, blank=True)
    slug = models.SlugField(max_length=220, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Carrera / programa"
        verbose_name_plural = "Carreras / programas"

    def __str__(self):
        return self.name


class AcademicPeriod(models.Model):
    """Período lectivo (ej. 2026-1)."""

    name = models.CharField("Nombre", max_length=64, unique=True)
    starts_on = models.DateField("Inicio", null=True, blank=True)
    ends_on = models.DateField("Fin", null=True, blank=True)
    is_current = models.BooleanField("Período actual", default=False, db_index=True)

    class Meta:
        ordering = ["-name"]
        verbose_name = "Período académico"
        verbose_name_plural = "Períodos académicos"

    def __str__(self):
        return self.name


class Offering(models.Model):
    """
    Curso académico ofertado: pertenece a carrera y período; tiene un docente responsable.
    """

    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name="offerings",
        verbose_name="Carrera",
    )
    period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.PROTECT,
        related_name="offerings",
        verbose_name="Período",
    )
    name = models.CharField("Nombre del curso", max_length=255)
    code = models.CharField("Código", max_length=64)
    semester = models.PositiveSmallIntegerField("Semestre", default=1)
    group = models.CharField("Grupo", max_length=16, default="A")
    credits = models.PositiveSmallIntegerField("Créditos", default=3)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="teaching_offerings",
        verbose_name="Docente responsable",
    )

    class Meta:
        ordering = ["-period__name", "program__name", "code"]
        verbose_name = "Curso ofertado"
        verbose_name_plural = "Cursos ofertados"
        constraints = [
            models.UniqueConstraint(
                fields=["program", "code", "period", "group"],
                name="academia_offering_unique_program_code_period_group",
            ),
        ]

    def __str__(self):
        return f"{self.code} · {self.name}"


class Enrollment(models.Model):
    """Inscripción / matrícula: estudiante en un curso ofertado."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Activa"
        WITHDRAWN = "withdrawn", "Baja"

    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Curso",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="academic_enrollments",
        verbose_name="Estudiante",
    )
    status = models.CharField(
        "Estado",
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    enrolled_at = models.DateTimeField("Fecha de inscripción", auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        constraints = [
            models.UniqueConstraint(
                fields=["offering", "student"],
                name="academia_enrollment_unique_offering_student",
            ),
        ]

    def __str__(self):
        return f"{self.student} → {self.offering.code}"
