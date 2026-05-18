# accounts/models.py
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from datetime import date


def student_profile_photo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"user_{instance.student.username}/profile_photo/{filename}"


def student_2fa_photo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"user_{instance.student.username}/profile_photo/{filename}"


# student model
class Student(AbstractUser):
    """
    Usuario del sistema EasyLearn. El rol determina el panel tras iniciar sesión.
    El rol determina el panel tras iniciar sesión.
    """

    class Role(models.TextChoices):
        STUDENT = "student", "Estudiante"
        TEACHER = "teacher", "Docente"
        ADMIN = "admin", "Administrador"

    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )
    academic_program = models.ForeignKey(
        "academia.Program",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
        verbose_name="Carrera / programa",
    )
    academic_semester = models.PositiveSmallIntegerField(
        "Semestre académico",
        null=True,
        blank=True,
    )

    def get_dashboard_url_name(self):
        if self.is_superuser or self.role == self.Role.ADMIN:
            return "dashboard_admin"
        if self.role == self.Role.TEACHER:
            return "dashboard_teacher"
        return "notes:dashboard"

    def save(self, *args, **kwargs):
        # Django admin exige is_staff para el rol administrador institucional.
        if self.is_superuser or self.role == self.Role.ADMIN:
            self.is_staff = True
        elif not self.is_superuser:
            self.is_staff = False
        super().save(*args, **kwargs)

    def age(self):
        today = date.today()
        age = (
            today.year
            - self.profile.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.profile.date_of_birth.month, self.profile.date_of_birth.day)
            )
        )
        return age


class Profile(models.Model):
    """
    Description: Student Profile Model
    """

    # choices for student year
    class StudentYear(models.TextChoices):
        FIRST = "1", "First Year"
        SECOND = "2", "Second Year"
        THIRD = "3", "Third Year"
        FOURTH = "4", "Fourth Year"
        FIFTH = "5", "Fifth Year"
        SIXTH = "6", "Sixth Year"

    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    degree = models.CharField(
        max_length=250, default="Not applicable", blank=True, null=True
    )

    date_of_birth = models.DateField(blank=True, null=True)

    year = models.CharField(
        max_length=2, choices=StudentYear.choices, default=StudentYear.FIRST
    )
    photo = models.ImageField(
        upload_to=student_profile_photo_path, blank=True, null=True
    )

    def get_absolute_url(self):
        return reverse(
            f"profile",
        )

    def __str__(self):
        return f"{self.student}'s profile"

    class Meta:
        ordering = ["student"]


class UserNotification(models.Model):
    """Aviso en campana del portal (calificación, fecha, aviso de curso)."""

    class Kind(models.TextChoices):
        GRADE = "grade", "Nueva calificación"
        DUE_DATE = "due_date", "Cambio de fecha"
        ANNOUNCEMENT = "announcement", "Aviso"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portal_notifications",
        verbose_name="Usuario",
    )
    kind = models.CharField(
        max_length=16,
        choices=Kind.choices,
        db_index=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    link = models.CharField("Enlace", max_length=500, blank=True)
    read_at = models.DateTimeField("Leída", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notificación del portal"
        verbose_name_plural = "Notificaciones del portal"

    def __str__(self):
        return f"{self.get_kind_display()}: {self.title}"

    @property
    def is_unread(self):
        return self.read_at is None
