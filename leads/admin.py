from django.contrib import admin
from django.utils.html import format_html
from .models import Lead, Business

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'business_type', 'source', 'status_colored', 'created_at')
    list_filter = ('status', 'source', 'business_type')
    search_fields = ('name', 'phone', 'email', 'business_type')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

    @admin.display(description='Status')
    def status_colored(self, obj):
        colors = {
            'new': '#3b82f6',        # Blue
            'contacted': '#f59e0b',  # Yellow/Orange
            'converted': '#10b981',  # Green
            'lost': '#ef4444'        # Red
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
