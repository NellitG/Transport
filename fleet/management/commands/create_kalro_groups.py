from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Create KALRO user groups"

    def handle(self, *args, **kwargs):
        groups = [
            "Employees",
            "Supervisors",
            "TransportOfficers",
            "Drivers",
            "Admins",
        ]

        for name in groups:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Group already exists: {name}"))

        self.stdout.write(self.style.SUCCESS("KALRO groups creation completed."))
