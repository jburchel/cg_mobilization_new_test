from django.contrib import admin
from .models import ComLog

@admin.register(ComLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ('contact', 'communication_type', 'date_created', 'summary_preview')
    list_filter = ('communication_type', 'date_created')
    search_fields = ('contact__first_name', 'contact__last_name', 'summary')
    date_hierarchy = 'date_created'

    def summary_preview(self, obj):
        return obj.summary[:50] + '...' if len(obj.summary) > 50 else obj.summary
    summary_preview.short_description = 'Summary'
