from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_sync_is_staff_for_admin_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserNotification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("grade", "Nueva calificación"),
                            ("due_date", "Cambio de fecha"),
                            ("announcement", "Aviso"),
                        ],
                        db_index=True,
                        max_length=16,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("message", models.TextField(blank=True)),
                ("link", models.CharField(blank=True, max_length=500, verbose_name="Enlace")),
                ("read_at", models.DateTimeField(blank=True, null=True, verbose_name="Leída")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portal_notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificación del portal",
                "verbose_name_plural": "Notificaciones del portal",
                "ordering": ["-created_at"],
            },
        ),
    ]
