from rest_framework import serializers
from .models import Lead

class LeadSerializer(serializers.ModelSerializer):
    bot_honey = serializers.CharField(required=False, write_only=True, allow_blank=True)

    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'whatsapp_sent', 'first_response_at']

    def validate_bot_honey(self, value):
        # Honeypot validation
        if value:
            raise serializers.ValidationError("Bot detected. Please remain off premises.")
        return value

    def validate(self, data):
        email = data.get('email')
        phone = data.get('phone')
        
        if email and phone:
            if Lead.objects.filter(email=email, phone=phone).exists():
                raise serializers.ValidationError("A lead with this email and phone already exists.")
        
        return data

    def validate_phone(self, value):
        value = value.replace(' ', '')
        if value.startswith('+971'):
            value = '0' + value[4:]
        return value
