from django.contrib.auth.models import Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Student


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
