from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

class Command(BaseCommand):
    help = 'Applies the userprofile migration'

    def handle(self, *args, **options):
        executor = MigrationExecutor(connection)
        app = 'userprofile'
        executor.migrate([(app, None)])
        self.stdout.write(self.style.SUCCESS('Successfully applied userprofile migration'))