import threading
import time

def send_whatsapp_notification(lead):
    """
    Mock function to simulate sending a WhatsApp message to the prospect.
    """
    def task():
        # Simulate network latency
        time.sleep(2)
        print(f"\n💬 [WHATSAPP MOCK] Message sent to {lead.phone}:\n"
              f"   'Hi {lead.name}, thanks for your interest! We received your request. "
              f"We'll be in touch shortly to help you with your {lead.business_type} needs.'\n")

    thread = threading.Thread(target=task)
    thread.daemon = True
    thread.start()

def send_email_notification(lead):
    """
    Mock function to simulate sending an email notification to the business owner.
    """
    def task():
        # Simulate network latency
        time.sleep(1)
        print(f"\n📧 [EMAIL MOCK] Notification to Business Owner:\n"
              f"   New Lead Alert! {lead.name} just filled the form.\n"
              f"   Phone: {lead.phone} | Email: {lead.email}\n"
              f"   Source: {lead.get_source_display()} | Please check the dashboard.\n")

    thread = threading.Thread(target=task)
    thread.daemon = True
    thread.start()
