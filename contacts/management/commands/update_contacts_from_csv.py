import csv
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Update contacts with data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('model', type=str, help='Model to update (Church or People)')
        parser.add_argument('id_field', type=str, help='Field to use as identifier (e.g., church_name or email)')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        model_name = options['model']
        id_field = options['id_field']

        # Get the model
        Model = apps.get_model('contacts', model_name)

        updated_count = 0
        not_found_count = 0

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                identifier = row.get(id_field)
                if not identifier:
                    self.stdout.write(self.style.WARNING(f"Row missing identifier '{id_field}': {row}"))
                    continue

                try:
                    obj = Model.objects.get(**{id_field: identifier})
                    for key, value in row.items():
                        if hasattr(obj, key) and value:
                            setattr(obj, key, value)
                    obj.save()
                    updated_count += 1
                except Model.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"{model_name} with {id_field}='{identifier}' not found"))
                    not_found_count += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} {model_name} records"))
        self.stdout.write(self.style.WARNING(f"Could not find {not_found_count} {model_name} records"))