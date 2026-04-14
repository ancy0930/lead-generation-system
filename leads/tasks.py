import logging
from celery import shared_task
import time
from .models import Lead

logger = logging.getLogger(__name__)

@shared_task
def send_whatsapp_notification(lead_id, phone, name, business_type):
    try:
        lead = Lead.objects.get(id=lead_id)
        if lead.whatsapp_sent:
            logger.info("Structured Log: Cancelled WhatsApp", extra={'lead_id': lead_id, 'action_type': 'whatsapp_skip', 'reason': 'already_sent'})
            return

        time.sleep(2)
        print(f"\n[CELERY WHATSAPP] Message sent to {phone}:\n"
              f"   'Hi {name}, thanks for contacting us. We will reach you shortly.'\n")
        
        lead.whatsapp_sent = True
        lead.save(update_fields=['whatsapp_sent'])
        
        logger.info("Structured Log: WhatsApp Sent", extra={'lead_id': lead_id, 'action_type': 'whatsapp_success'})

    except Lead.DoesNotExist:
        logger.error("Structured Log: Invalid Task", extra={'lead_id': lead_id, 'action_type': 'whatsapp_fail', 'reason': 'not_found'})

@shared_task
def send_email_notification(lead_id, email, name, phone, source_display):
    time.sleep(1)
    print(f"\n[CELERY EMAIL] Notification to Business Owner:\n"
          f"   New Lead Alert! {name} just filled the form.\n"
          f"   Phone: {phone} | Email: {email}\n"
          f"   Source: {source_display} | Please check the dashboard.\n")
    logger.info("Structured Log: Email Sent", extra={'lead_id': lead_id, 'action_type': 'email_success'})
