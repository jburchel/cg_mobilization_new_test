from django.contrib import admin
from .models import Contact, People, Church

@admin.register(Contact)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'email', 'phone', 'city', 'state')
    search_fields = ('church_name', 'first_name', 'last_name', 'email')
    list_filter = ('state', 'preferred_contact_method')

    def get_name(self, obj):
        if hasattr(obj, 'church'):
            return obj.church.church_name
        elif hasattr(obj, 'people'):
            return f"{obj.people.first_name} {obj.people.last_name}".strip()
        else:
            return obj.church_name or f"{obj.first_name} {obj.last_name}".strip() or "Unnamed Contact"
    get_name.short_description = 'Name'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('church', 'people')

    fieldsets = (
        ('Contact Information', {
            'fields': ('church_name', 'first_name', 'last_name', 'email', 'phone', 'preferred_contact_method')
        }),
        ('Address', {
            'fields': ('street_address', 'city', 'state', 'zip_code')
        }),
        ('Additional Information', {
            'fields': ('initial_notes', 'image')
        }),
        ('Dates', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('date_created', 'date_modified')

@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'phone', 'get_church_name', 'people_pipeline', 'priority', 'assigned_to')
    search_fields = ('first_name', 'last_name', 'email', 'church_name', 'affiliated_church__church_name')
    list_filter = ('people_pipeline', 'priority', 'assigned_to', 'marital_status', 'color')
    autocomplete_fields = ['affiliated_church']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Name'

    def get_church_name(self, obj):
        return obj.affiliated_church.church_name if obj.affiliated_church else obj.church_name
    get_church_name.short_description = 'Church'

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'preferred_contact_method')
        }),
        ('Church Affiliation', {
            'fields': ('church_name', 'affiliated_church'),
            'description': "Enter a church name or select an affiliated church from the database."
        }),
        ('Address', {
            'fields': ('street_address', 'city', 'state', 'zip_code', 'home_country')
        }),
        ('CRM Details', {
            'fields': ('color', 'people_pipeline', 'priority', 'assigned_to', 'source')
        }),
        ('Family Information', {
            'fields': ('marital_status', 'spouse_recruit')
        }),
        ('Recruitment Information', {
            'fields': ('desired_service', 'info_given')
        }),
        ('Additional Information', {
            'fields': ('virtuous', 'image', 'initial_notes', 'referred_by')
        }),
        ('Dates', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',)
        }),
        ('Closure Information', {
            'fields': ('reason_closed', 'date_closed'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('date_created', 'date_modified')

    def save_model(self, request, obj, form, change):
        if obj.affiliated_church and not obj.church_name:
            obj.church_name = obj.affiliated_church.church_name
        super().save_model(request, obj, form, change)

@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'email', 'phone', 'church_pipeline', 'priority', 'assigned_to')
    search_fields = ('church_name', 'email', 'senior_pastor_last_name')
    list_filter = ('church_pipeline', 'priority', 'assigned_to', 'denomination', 'color')
    
    # Fields to exclude from the form
    exclude = ('first_name', 'last_name')

    # Organize fields into fieldsets
    fieldsets = (
        ('Church Information', {
            'fields': ('church_name', 'website', 'denomination', 'congregation_size', 'year_founded')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'preferred_contact_method', 'street_address', 'city', 'state', 'zip_code')
        }),
        ('Key People', {
            'fields': (
                'primary_contact_first_name', 'primary_contact_last_name',
                'senior_pastor_first_name', 'senior_pastor_last_name',
                'missions_pastor_first_name', 'missions_pastor_last_name'
            )
        }),
        ('CRM Details', {
            'fields': ('color', 'church_pipeline', 'priority', 'assigned_to', 'source', 'referred_by')
        }),
        ('Additional Information', {
            'fields': ('info_given', 'initial_notes', 'virtuous', 'image')
        }),
        ('Closure Information', {
            'fields': ('reason_closed', 'date_closed'),
            'classes': ('collapse',)  # This fieldset will be collapsible
        })
    )
