from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Task, ActivityLog

@receiver(post_save, sender=Task)
def log_task_created_or_updated(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.user,
            action=f"Created task: {instance.title}"
        )
    else:
        ActivityLog.objects.create(
            user=instance.user,
            action=f"Updated task: {instance.title}"
        )

@receiver(post_delete, sender=Task)
def log_task_deleted(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.user,
        action=f"Deleted task: {instance.title}"
    )

