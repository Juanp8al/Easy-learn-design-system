# Generated manually — alinea is_staff con rol administrador para acceso a /admin/

from django.db import migrations


def sync_staff_for_mer_admins(apps, schema_editor):
    Student = apps.get_model("accounts", "Student")
    Permission = apps.get_model("auth", "Permission")

    Student.objects.filter(role="admin").update(is_staff=True)
    Student.objects.filter(is_superuser=True).update(is_staff=True)

    perms = list(Permission.objects.all())
    for student in Student.objects.filter(role="admin").iterator():
        student.user_permissions.set(perms)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_student_academic_program_student_academic_semester"),
    ]

    operations = [
        migrations.RunPython(sync_staff_for_mer_admins, noop_reverse),
    ]
