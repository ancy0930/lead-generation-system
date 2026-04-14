from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Business(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    )
    
    SOURCE_CHOICES = (
        ('website', 'Website'),
        ('instagram', 'Instagram'),
        ('google', 'Google'),
        ('other', 'Other'),
    )

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='leads', null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    business_type = models.CharField(max_length=255, blank=True, null=True, help_text="Industry or type of business")
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='website')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True, null=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    whatsapp_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def source_category(self):
        mapping = {
            'instagram': 'social',
            'google': 'search',
            'website': 'direct',
        }
        return mapping.get(self.source, 'other')

    def save(self, *args, **kwargs):
        if self.pk:
            orig = Lead.objects.get(pk=self.pk)
            if orig.status != 'contacted' and self.status == 'contacted' and not self.first_response_at:
                self.first_response_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.phone}"
