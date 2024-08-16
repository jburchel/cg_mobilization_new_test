from django.contrib import admin
from .models import CommunicationLog

@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ('contact', 'communication_type', 'date', 'summary_preview')
    list_filter = ('communication_type', 'date')
    search_fields = ('contact__first_name', 'contact__last_name', 'summary')
    date_hierarchy = 'date'

    def summary_preview(self, obj):
        return obj.summary[:50] + '...' if len(obj.summary) > 50 else obj.summary
    summary_preview.short_description = 'Summary'
