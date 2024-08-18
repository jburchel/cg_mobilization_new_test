from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from task_tracker.models import Task
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample tasks for the task tracker'

    def handle(self, *args, **options):
        # Ensure we have at least one user
        user, created = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})
        if created:
            user.set_password('adminpassword')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # List of sample task titles
        task_titles = [
            "Prepare project proposal", "Schedule team meeting", "Review code changes",
            "Update documentation", "Fix critical bug", "Implement new feature",
            "Conduct user testing", "Optimize database queries", "Create backup strategy",
            "Design new user interface", "Refactor legacy code", "Write unit tests",
            "Set up continuous integration", "Perform security audit", "Plan sprint goals"
        ]

        # Create tasks
        for _ in range(20):  # Create 20 sample tasks
            Task.objects.create(
                title=random.choice(task_titles),
                description=f"This is a sample task description for {random.choice(task_titles).lower()}.",
                status=random.choice([choice[0] for choice in Task.STATUS_CHOICES]),
                priority=random.choice([choice[0] for choice in Task.PRIORITY_CHOICES]),
                assigned_to=user,
                created_by=user,
                due_date=timezone.now().date() + timezone.timedelta(days=random.randint(1, 30))
            )

        self.stdout.write(self.style.SUCCESS('Successfully created 20 sample tasks'))