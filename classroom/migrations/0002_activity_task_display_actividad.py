"""Renombra títulos demo «Tarea …» → «Actividad …» (etiqueta de tipo ya es Actividad/Taller en código)."""

from django.db import migrations


def rename_demo_tarea_titles(apps, schema_editor):
    Activity = apps.get_model("classroom", "Activity")
    for act in Activity.objects.filter(title__startswith="Tarea "):
        act.title = "Actividad " + act.title[6:]
        act.save(update_fields=["title"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("classroom", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(rename_demo_tarea_titles, noop),
    ]
