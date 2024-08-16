from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Reset all test data in the database'

    def handle(self, *args, **options):
        # List of app names to reset, in the order they should be reset
        apps_to_reset = ['com_log', 'contacts']

        with connection.cursor() as cursor:
            # Temporarily disable foreign key constraints
            if connection.vendor == 'sqlite':
                cursor.execute("PRAGMA foreign_keys = OFF;")
            elif connection.vendor == 'postgresql':
                cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
            elif connection.vendor == 'mysql':
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            for app_name in apps_to_reset:
                app_config = apps.get_app_config(app_name)
                for model in app_config.get_models():
                    table_name = model._meta.db_table
                    self.stdout.write(f"Deleting all data from {table_name}")
                    cursor.execute(f"DELETE FROM {table_name}")
                    
                    # Reset the auto-increment counter
                    if connection.vendor == 'sqlite':
                        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
                    elif connection.vendor == 'postgresql':
                        cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1")
                    elif connection.vendor == 'mysql':
                        cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")

            # Re-enable foreign key constraints
            if connection.vendor == 'sqlite':
                cursor.execute("PRAGMA foreign_keys = ON;")
            elif connection.vendor == 'postgresql':
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE;")
            elif connection.vendor == 'mysql':
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        self.stdout.write(self.style.SUCCESS('All test data has been reset successfully'))