"""Señales del modelo académico."""

from django.db.models.signals import pre_save
from django.dispatch import receiver

from academia.models import AcademicPeriod


@receiver(pre_save, sender=AcademicPeriod)
def ensure_single_current_period(sender, instance, **kwargs):
    if instance.is_current:
        AcademicPeriod.objects.exclude(pk=instance.pk).update(is_current=False)
