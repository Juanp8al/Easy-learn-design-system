from django.contrib.auth.models import Permission
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import Student
from accounts.notifications import (
    notify_announcement,
    notify_due_date_changed,
    notify_grade_published,
)


@receiver(post_save, sender=Student)
def sync_mer_admin_django_permissions(sender, instance, **kwargs):
    """
    Usuarios con rol administrador en EasyLearn deben poder usar /admin/.
    Django exige is_staff (lo pone Student.save) y permisos por modelo.
    """
    if instance.is_superuser or instance.role != Student.Role.ADMIN or not instance.is_staff:
        return
    perms = Permission.objects.all()
    if not perms.exists():
        return
    perm_ids = set(perms.values_list("pk", flat=True))
    existing = set(instance.user_permissions.values_list("pk", flat=True))
    if perm_ids <= existing:
        return
    instance.user_permissions.set(perms)


@receiver(post_save, sender="classroom.Grade")
def on_grade_saved(sender, instance, created, **kwargs):
    if created:
        notify_grade_published(instance)


@receiver(post_save, sender="classroom.Announcement")
def on_announcement_saved(sender, instance, created, **kwargs):
    if created:
        notify_announcement(instance)


@receiver(pre_save, sender="classroom.Activity")
def capture_activity_due_before_save(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_due_at = None
        return
    try:
        previous = sender.objects.only("due_at").get(pk=instance.pk)
        instance._previous_due_at = previous.due_at
    except sender.DoesNotExist:
        instance._previous_due_at = None


@receiver(post_save, sender="classroom.Activity")
def on_activity_saved(sender, instance, created, **kwargs):
    if created:
        return
    previous = getattr(instance, "_previous_due_at", None)
    notify_due_date_changed(instance, previous)
