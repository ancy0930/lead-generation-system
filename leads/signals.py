from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead
from .tasks import send_whatsapp_notification, send_email_notification

@receiver(post_save, sender=Lead)
def lead_post_save(sender, instance, created, **kwargs):
    if created:
        # Trigger Celery tasks asynchronously
        send_whatsapp_notification.delay(
            instance.id, instance.phone, instance.name, instance.business_type
        )
        send_email_notification.delay(
            instance.id, instance.email, instance.name, instance.phone, instance.get_source_display()
        )
