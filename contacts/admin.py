from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from import_export.admin import ImportExportModelAdmin
from import_export.forms import ImportForm
from django import forms
from .models import Contact, People, Church
from datetime import datetime

class CustomDateWidget(DateWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            try:
                return datetime.strptime(value, '%m/%d/%y').date()
            except ValueError:
                return super().clean(value, row, *args, **kwargs)
        return None

class CustomImportForm(ImportForm):
    import_file = forms.FileField(
        label='Select a CSV file to import',
        help_text='The file must be in CSV format.',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )

    def __init__(self, import_formats, *args, **kwargs):
        super().__init__(import_formats, *args, **kwargs)

class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact
        fields = ('id', 'church_name', 'first_name', 'last_name', 'email', 'phone', 'preferred_contact_method',
                  'street_address', 'city', 'state', 'zip_code', 'initial_notes', 'date_created', 'date_modified')

class ChurchResource(ContactResource):
    date_created = fields.Field(attribute='date_created', widget=CustomDateWidget())
    date_modified = fields.Field(attribute='date_modified', widget=CustomDateWidget())
    date_closed = fields.Field(attribute='date_closed', widget=CustomDateWidget())

    class Meta(ContactResource.Meta):
        model = Church
        import_id_fields = ('church_name',)
        fields = ContactResource.Meta.fields + ('virtuous', 'senior_pastor_first_name', 'senior_pastor_last_name',
                                                'senior_pastor_phone', 'senior_pastor_email', 'missions_pastor_first_name',
                                                'missions_pastor_last_name', 'mission_pastor_phone', 'mission_pastor_email',
                                                'primary_contact_first_name', 'primary_contact_last_name',
                                                'primary_contact_phone', 'primary_contact_email', 'website',
                                                'denomination', 'congregation_size', 'color', 'church_pipeline',
                                                'priority', 'assigned_to', 'source', 'referred_by', 'info_given',
                                                'reason_closed', 'year_founded', 'date_closed')
        skip_unchanged = True
        report_skipped = False

    def before_import_row(self, row, **kwargs):
        for field in self.fields.keys():
            if field not in row:
                row[field] = None

    def import_obj(self, obj, data, dry_run):
        for field, value in data.items():
            if value is not None:
                setattr(obj, field, value)
        return super().import_obj(obj, data, dry_run)

class PeopleResource(ContactResource):
    date_created = fields.Field(attribute='date_created', widget=CustomDateWidget())
    date_modified = fields.Field(attribute='date_modified', widget=CustomDateWidget())
    date_closed = fields.Field(attribute='date_closed', widget=CustomDateWidget())
    affiliated_church = fields.Field(
        column_name='affiliated_church',
        attribute='affiliated_church',
        widget=ForeignKeyWidget(Church, 'church_name')
    )

    class Meta(ContactResource.Meta):
        model = People
        import_id_fields = ('first_name', 'last_name', 'email')
        fields = ContactResource.Meta.fields + ('affiliated_church', 'virtuous', 'home_country', 'spouse_recruit',
                                                'marital_status', 'spouse_first_name', 'spouse_last_name', 
                                                'people_pipeline', 'priority', 'assigned_to','source', 'referred_by', 
                                                'person_type','info_given', 'desired_service', 'reason_closed','date_closed')
        skip_unchanged = True
        report_skipped = False

    def before_import_row(self, row, **kwargs):
        for field in self.fields.keys():
            if field not in row:
                row[field] = None

    def import_obj(self, obj, data, dry_run):
        for field, value in data.items():
            if value is not None:
                setattr(obj, field, value)
        return super().import_obj(obj, data, dry_run)

@admin.register(Contact)
class ContactsAdmin(ImportExportModelAdmin):
    resource_class = ContactResource
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
class PeopleAdmin(ImportExportModelAdmin):
    resource_class = PeopleResource
    import_form_class = CustomImportForm
    list_display = ('get_full_name', 'email', 'phone', 'get_church_name', 'people_pipeline', 'priority', 'assigned_to')
    search_fields = ('first_name', 'last_name', 'email', 'church_name', 'affiliated_church__church_name')
    list_filter = ('people_pipeline', 'priority', 'assigned_to', 'marital_status','person_type')
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
            'fields': ('people_pipeline', 'priority', 'assigned_to', 'source','person_type')
        }),
        ('Family Information', {
            'fields': ('marital_status', 'spouse_first_name', 'spouse_last_name',)
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
class ChurchAdmin(ImportExportModelAdmin):
    resource_class = ChurchResource
    import_form_class = CustomImportForm
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
        ('Dates', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',)
        }),
        ('Closure Information', {
            'fields': ('reason_closed', 'date_closed'),
            'classes': ('collapse',)  # This fieldset will be collapsible
        })
    )
    
    readonly_fields = ('date_created', 'date_modified')