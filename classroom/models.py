"""
Aula virtual: semanas, materiales, actividades, entregas y calificaciones
vinculadas a un curso ofertado (academia.Offering).
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class AcademicWeek(models.Model):
    """Semana académica dentro de un curso ofertado."""

    class Status(models.TextChoices):
        LOCKED = "locked", "Bloqueada"
        AVAILABLE = "available", "Disponible"
        IN_PROGRESS = "in_progress", "En curso"
        COMPLETED = "completed", "Completada"

    offering = models.ForeignKey(
        "academia.Offering",
        on_delete=models.CASCADE,
        related_name="academic_weeks",
        verbose_name="Curso ofertado",
    )
    week_number = models.PositiveSmallIntegerField("Número de semana")
    title = models.CharField("Tema", max_length=255)
    description = models.TextField("Descripción", blank=True)
    starts_on = models.DateField("Inicio", null=True, blank=True)
    ends_on = models.DateField("Fin", null=True, blank=True)
    status = models.CharField(
        "Estado",
        max_length=16,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    class Meta:
        ordering = ["offering", "week_number"]
        verbose_name = "Semana académica"
        verbose_name_plural = "Semanas académicas"
        constraints = [
            models.UniqueConstraint(
                fields=["offering", "week_number"],
                name="classroom_week_unique_offering_number",
            ),
        ]

    def __str__(self):
        return f"{self.offering.code} · Semana {self.week_number}"


class StudyMaterial(models.Model):
    """Material de estudio publicado en una semana."""

    class MaterialType(models.TextChoices):
        DOCUMENT = "document", "Documento"
        VIDEO = "video", "Video"
        IMAGE = "image", "Imagen"
        LINK = "link", "Enlace"
        PRESENTATION = "presentation", "Presentación"
        OTHER = "other", "Otro"

    week = models.ForeignKey(
        AcademicWeek,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Semana",
    )
    title = models.CharField("Título", max_length=255)
    description = models.TextField("Descripción", blank=True)
    material_type = models.CharField(
        "Tipo",
        max_length=16,
        choices=MaterialType.choices,
        default=MaterialType.DOCUMENT,
    )
    file = models.FileField(
        "Archivo",
        upload_to="classroom/materials/%Y/%m/",
        blank=True,
        null=True,
    )
    external_url = models.URLField("Enlace externo", blank=True)
    is_required = models.BooleanField("Obligatorio", default=True)
    published_at = models.DateTimeField("Publicado", default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materials_created",
        verbose_name="Publicado por",
    )

    class Meta:
        ordering = ["week", "title"]
        verbose_name = "Material de estudio"
        verbose_name_plural = "Materiales de estudio"

    def __str__(self):
        return self.title


class Activity(models.Model):
    """Actividad académica (actividad, taller, quiz, foro, etc.)."""

    class ActivityType(models.TextChoices):
        TASK = "task", "Actividad"
        WORKSHOP = "workshop", "Taller"
        FORUM = "forum", "Foro"
        QUIZ = "quiz", "Cuestionario"
        EXAM = "exam", "Examen"
        PRACTICE = "practice", "Práctica"
        DELIVERY = "delivery", "Entrega"

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicada"
        CLOSED = "closed", "Cerrada"

    week = models.ForeignKey(
        AcademicWeek,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Semana",
    )
    title = models.CharField("Título", max_length=255)
    description = models.TextField("Descripción", blank=True)
    instructions = models.TextField("Instrucciones", blank=True)
    activity_type = models.CharField(
        "Tipo",
        max_length=16,
        choices=ActivityType.choices,
        default=ActivityType.TASK,
    )
    due_at = models.DateTimeField("Fecha límite", null=True, blank=True)
    status = models.CharField(
        "Estado",
        max_length=16,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )
    allows_draft = models.BooleanField("Permite borrador", default=True)
    allow_late = models.BooleanField("Permite entrega tardía", default=False)
    max_score = models.DecimalField(
        "Puntaje máximo",
        max_digits=4,
        decimal_places=2,
        default=5.0,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities_created",
        verbose_name="Creada por",
    )

    class Meta:
        ordering = ["week", "due_at", "title"]
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"

    def __str__(self):
        return self.title

    @property
    def offering(self):
        return self.week.offering


class Submission(models.Model):
    """Entrega de un estudiante a una actividad."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        SUBMITTED = "submitted", "Entregada"
        LATE = "late", "Tardía"
        GRADED = "graded", "Calificada"

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Actividad",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_submissions",
        verbose_name="Estudiante",
    )
    file = models.FileField(
        "Archivo",
        upload_to="classroom/submissions/%Y/%m/",
        blank=True,
        null=True,
    )
    comment = models.TextField("Comentario", blank=True)
    is_draft = models.BooleanField("Es borrador", default=True)
    submitted_at = models.DateTimeField("Fecha de entrega", null=True, blank=True)
    status = models.CharField(
        "Estado",
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    class Meta:
        ordering = ["-submitted_at", "-id"]
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "student"],
                name="classroom_submission_unique_activity_student",
            ),
        ]

    def __str__(self):
        return f"{self.student} → {self.activity.title}"


class Grade(models.Model):
    """Calificación de una entrega."""

    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name="grade",
        verbose_name="Entrega",
    )
    score = models.DecimalField("Nota", max_digits=4, decimal_places=2)
    feedback = models.TextField("Retroalimentación", blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grades_given",
        verbose_name="Calificado por",
    )
    graded_at = models.DateTimeField("Fecha de calificación", auto_now_add=True)

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"

    def __str__(self):
        return f"{self.score} · {self.submission}"


class Announcement(models.Model):
    """Aviso del docente en un curso o semana."""

    class Priority(models.TextChoices):
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"

    offering = models.ForeignKey(
        "academia.Offering",
        on_delete=models.CASCADE,
        related_name="announcements",
        verbose_name="Curso ofertado",
    )
    week = models.ForeignKey(
        AcademicWeek,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="announcements",
        verbose_name="Semana",
    )
    title = models.CharField("Título", max_length=255)
    content = models.TextField("Contenido")
    priority = models.CharField(
        "Prioridad",
        max_length=8,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    published_at = models.DateTimeField("Publicado", default=timezone.now)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements_authored",
        verbose_name="Autor",
    )

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"

    def __str__(self):
        return self.title


class Forum(models.Model):
    """Foro de discusión asociado a una semana."""

    class Status(models.TextChoices):
        OPEN = "open", "Abierto"
        CLOSED = "closed", "Cerrado"

    week = models.ForeignKey(
        AcademicWeek,
        on_delete=models.CASCADE,
        related_name="forums",
        verbose_name="Semana",
    )
    title = models.CharField("Título", max_length=255)
    description = models.TextField("Descripción", blank=True)
    status = models.CharField(
        "Estado",
        max_length=8,
        choices=Status.choices,
        default=Status.OPEN,
    )
    published_at = models.DateTimeField("Publicado", default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forums_created",
        verbose_name="Creado por",
    )

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Foro"
        verbose_name_plural = "Foros"

    def __str__(self):
        return self.title
