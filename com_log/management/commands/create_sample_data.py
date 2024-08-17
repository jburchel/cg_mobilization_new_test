import random
from django.core.management.base import BaseCommand
from contacts.models import Church, People
from django.contrib.auth import get_user_model
from django.utils import timezone

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample data for Churches and People'

    def handle(self, *args, **kwargs):
        self.create_churches()
        self.create_people()
        self.stdout.write(self.style.SUCCESS('Sample data has been created successfully'))

    def create_churches(self):
        church_names = [
            "Grace Community Church", "Lighthouse Baptist", "New Life Assembly",
            "Calvary Chapel", "First Baptist Church", "Hope Community Church",
            "St. Mary's Catholic Church", "Crossroads Community Church",
            "Trinity Lutheran Church", "Bethel Church"
        ]

        for name in church_names:
            church = Church.objects.create(
                church_name=name,
                email=f"info@{name.lower().replace(' ', '')}.org",
                phone=f"({random.randint(100,999)})-{random.randint(100,999)}-{random.randint(1000,9999)}",
                preferred_contact_method=random.choice([choice[0] for choice in Church.PREFERRED_CONTACT_METHODS]),
                street_address=f"{random.randint(100,9999)} Main St",
                city=random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                state=random.choice([choice[0] for choice in Church.STATE]),
                zip_code=f"{random.randint(10000,99999)}",
                senior_pastor_first_name=random.choice(["John", "Michael", "David", "Robert", "William"]),
                senior_pastor_last_name=random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"]),
                senior_pastor_phone=f"({random.randint(100,999)})-{random.randint(100,999)}-{random.randint(1000,9999)}",
                senior_pastor_email=f"pastor@{name.lower().replace(' ', '')}.org",
                primary_contact_first_name=random.choice(["Sarah", "Emily", "Jessica", "Lauren", "Ashley"]),
                primary_contact_last_name=random.choice(["Davis", "Miller", "Wilson", "Moore", "Taylor"]),
                primary_contact_phone=f"({random.randint(100,999)})-{random.randint(100,999)}-{random.randint(1000,9999)}",
                primary_contact_email=f"contact@{name.lower().replace(' ', '')}.org",
                website=f"https://www.{name.lower().replace(' ', '')}.org",
                denomination=random.choice(["Baptist", "Catholic", "Lutheran", "Non-denominational", "Presbyterian"]),
                congregation_size=random.randint(50, 5000),
                color=random.choice([choice[0] for choice in Church.COLOR]),
                church_pipeline=random.choice([choice[0] for choice in Church.CHURCH_PIPELINE_CHOICES]),
                priority=random.choice([choice[0] for choice in Church.PRIORITY]),
                assigned_to=random.choice([choice[0] for choice in Church.ASSIGNED_TO_CHOICES]),
                source=random.choice([choice[0] for choice in Church.SOURCE]),
                info_given="Sample church information",
                year_founded=random.randint(1800, 2020),
            )
            self.stdout.write(self.style.SUCCESS(f'Created church: {church.church_name}'))

    def create_people(self):
        first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

        for i in range(10):
            person = People.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                email=f"{first_names[i].lower()}.{last_names[i].lower()}@example.com",
                phone=f"({random.randint(100,999)})-{random.randint(100,999)}-{random.randint(1000,9999)}",
                preferred_contact_method=random.choice([choice[0] for choice in People.PREFERRED_CONTACT_METHODS]),
                street_address=f"{random.randint(100,9999)} Oak St",
                city=random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                state=random.choice([choice[0] for choice in People.STATE]),
                zip_code=f"{random.randint(10000,99999)}",
                church_name=f"{random.choice(['First', 'Second', 'Third'])} {random.choice(['Baptist', 'Presbyterian', 'Methodist'])} Church",
                home_country="United States",
                marital_status=random.choice([choice[0] for choice in People.MARITAL_STATUS]),
                color=random.choice([choice[0] for choice in People.COLOR]),
                people_pipeline=random.choice([choice[0] for choice in People.PEOPLE_PIPELINE]),
                priority=random.choice([choice[0] for choice in People.PRIORITY]),
                assigned_to=random.choice([choice[0] for choice in People.ASSIGNED_TO]),
                source=random.choice([choice[0] for choice in People.SOURCE]),
                info_given="Sample person information",
                desired_service="Sample desired service",
                initial_notes="Sample initial notes",
            )
            self.stdout.write(self.style.SUCCESS(f'Created person: {person.first_name} {person.last_name}'))